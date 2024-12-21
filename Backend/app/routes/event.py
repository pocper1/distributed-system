import os
import uuid
import base64
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_postgresql_connection, get_redis_connection, celery_app
from models import Event, Team, User, Checkin, Score
from models.association import user_teams
from request.main import (
    CreateEventRequest,
    UploadRequest,
    UserCheckinRequest,
    CreateTeamRequest,
    JoinTeamRequest,
    UpdateScoreRequest
)
from services.score_service import calculate_team_score
from google.cloud import storage
from redis import Redis
from tasks import create_checkin_records_task, upload_to_gcp_task, create_team_task, join_team_task, calculate_team_score_task, persist_team_scores_task
import aiofiles

# Define router
router = APIRouter()

# Global settings
utc_plus_8 = timezone(timedelta(hours=8))
redis_conn: Redis = get_redis_connection()


# ------------------ Utility Functions ------------------

def upload_to_tmp(file_data: bytes, file_name: str) -> str:
    """
    Upload the file to local /tmp (dev environment).
    """
    tmp_path = os.path.join("/tmp", file_name)
    with open(tmp_path, 'wb') as f:
        f.write(file_data)
    # Return the local path or a dev-accessible URL
    return tmp_path


def is_dev_env() -> bool:
    """
    Return True if the environment is dev; False if production.
    """
    env_name = os.getenv("ENV", "dev").lower()
    return env_name == "dev"


def check_upload_status(async_result, checkin_id: int, db_session: Session):
    """
    Check the status of the Celery task and update the Checkin record with the photo URL.
    """
    if async_result.ready():
        try:
            upload_url = async_result.get()
            # Update the Checkin record with the photo URL
            checkin = db_session.query(Checkin).filter(
                Checkin.id == checkin_id).first()
            if checkin:
                checkin.photo_url = upload_url
                db_session.commit()
        except Exception as e:
            # Handle exceptions, possibly log them
            pass


def is_event_active(event_id: int, db: Session):
    """
    Check if the event is currently active (ongoing).
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise ValueError("Event not found")
    current_time = datetime.now(timezone.utc)
    return event.start_time <= current_time <= event.end_time


def get_team_score_from_cache(team_id: int) -> float:
    """
    Retrieve the team's score from Redis. If not available, calculate and cache it.
    """
    score = redis_conn.get(f"team:{team_id}:score")
    if score is not None:
        return float(score)

    # If not in Redis, calculate score from the database
    score = calculate_team_score(team_id)
    redis_conn.set(f"team:{team_id}:score", score,
                   ex=3600)  # Cache score for 1 hour
    return score


# ------------------ Event Routes ------------------


@router.post("/api/event/create", summary="Create Event", tags=["Event"])
def create_event(request: CreateEventRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Create a new event.
    """
    if request.start_time >= request.end_time:
        raise HTTPException(
            status_code=400, detail="Start time must be before end time")

    current_time = datetime.now(timezone.utc)
    new_event = Event(
        name=request.name,
        description=request.description,
        start_time=request.start_time.astimezone(timezone.utc),
        end_time=request.end_time.astimezone(timezone.utc),
        created_at=current_time
    )
    try:
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return {"message": "Event created successfully", "event_id": new_event.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create event")


@router.post("/api/event/{event_id}/upload", summary="Upload Check-in Data", tags=["Event"])
def upload_checkin(event_id: int, request: UploadRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Upload check-in data for all teams a user belongs to in a specific event.
    """
    try:
        # Verify if the event is active
        if not is_event_active(event_id, db):
            raise HTTPException(
                status_code=404, detail="Event is not active or does not exist.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Query all teams the user belongs to in this event
    user_teams_query = db.query(Team).join(user_teams).filter(
        user_teams.c.user_id == request.user_id,
        Team.event_id == event_id
    ).all()

    if not user_teams_query:
        raise HTTPException(
            status_code=404,
            detail="The user does not belong to any teams in this event."
        )

    # Upload photo based on environment
    photo_url = None
    if request.photo:
        try:
            file_data = base64.b64decode(request.photo)
            file_name = f"checkin_photos/{uuid.uuid4()}.png"
            env = os.getenv("ENV", "local").lower()

            if env == "local":
                # Upload to /tmp for local environment
                tmp_path = upload_to_tmp(file_data, file_name)
                photo_url = f"file://{tmp_path}"
            else:
                # Upload to GCP Cloud Storage
                bucket_name = os.environ.get("GCP_BUCKET_NAME")
                if not bucket_name:
                    raise EnvironmentError(
                        "GCP_BUCKET_NAME environment variable is not set.")

                # Dispatch background task to upload the photo to GCP
                async_result = upload_to_gcp_task.delay(
                    bucket_name, file_data, file_name)
                photo_url = f"Processing upload: {file_name}"  # Placeholder
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to process photo upload: {str(e)}"
            )

    # Extract team IDs from the query result
    team_ids = [team.id for team in user_teams_query]

    # Dispatch background task to create check-in records
    create_checkin_records_task.delay(
        user_id=request.user_id,
        team_ids=team_ids,
        comment=request.comment,
        photo_url=photo_url
    )

    return {
        "message": "Check-in data upload initiated successfully. Check-in records are being created in the background."
    }


@router.get("/api/event/{event_id}/upload/list", summary="Get All Uploads for Event", tags=["Event"])
def get_event_uploads(event_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Retrieve all uploads (photos and comments) for a specific event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    uploads = (
        db.query(Checkin)
        .join(Team, Team.id == Checkin.team_id)
        .filter(Team.event_id == event_id)
        .all()
    )

    if not uploads:
        return {"uploads": []}

    return {
        "uploads": [
            {
                "user_id": upload.user_id,
                "team_id": upload.team_id,
                "comment": upload.content,
                "photo_url": upload.photo_url,
                "created_at": upload.created_at.astimezone(utc_plus_8).isoformat(),
            }
            for upload in uploads
        ]
    }


@router.get("/api/event/all", summary="Get All Events", tags=["Event"])
def get_events(db: Session = Depends(get_postgresql_connection)):
    """
    Retrieve all events sorted by created_at in descending order with a limit.
    """
    events = (
        db.query(Event.id, Event.name, Event.start_time,
                 Event.end_time, Event.created_at)
        .order_by(Event.created_at.desc())
        .limit(10)
        .all()
    )
    return {
        "events": [
            {
                "id": event.id,
                "name": event.name,
                "start_time": event.start_time.astimezone(utc_plus_8).isoformat() if event.start_time else None,
                "end_time": event.end_time.astimezone(utc_plus_8).isoformat() if event.end_time else None,
                "created_at": event.created_at.astimezone(utc_plus_8).isoformat() if event.created_at else None,
            }
            for event in events
        ]
    }


@router.get("/api/event/{event_id}", summary="Get Event by ID", tags=["Event"])
def get_event(event_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Retrieve a specific event by its ID.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "start_time": event.start_time.astimezone(utc_plus_8).isoformat() if event.start_time else None,
        "end_time": event.end_time.astimezone(utc_plus_8).isoformat() if event.end_time else None,
        "created_at": event.created_at.astimezone(utc_plus_8).isoformat() if event.created_at else None,
    }


@router.post("/api/event/{event_id}/checkin", summary="User Check-in for Event", tags=["Event", "Checkin"])
def user_checkin(event_id: int, request: UserCheckinRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Record a check-in for a user in a specific event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    team = db.query(Team).filter(Team.id == request.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    user_team = db.query(user_teams).filter(
        user_teams.c.user_id == request.user_id,
        user_teams.c.team_id == request.team_id
    ).first()
    if not user_team:
        raise HTTPException(
            status_code=403, detail="User does not belong to this team")

    new_checkin = Checkin(
        user_id=request.user_id,
        team_id=request.team_id,
        content=request.content
    )
    db.add(new_checkin)
    db.commit()
    db.refresh(new_checkin)
    return {"message": "Check-in recorded successfully", "checkin_id": new_checkin.id}


# ------------------ Team Routes ------------------

@router.post("/api/event/{event_id}/team/create", summary="Create Team for Event", tags=["Event", "Team"])
def create_team(event_id: int, request: CreateTeamRequest):
    """
    Dispatch a task to create a new team for a specific event.
    """
    async_result = create_team_task.delay(
        event_id, request.name, request.description)
    return {"message": "Team creation initiated", "task_id": async_result.id}


@router.get("/api/user/{user_id}/teams", summary="Get User Teams", tags=["User"])
def get_user_teams(user_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Get all teams the user has joined.
    """
    teams = db.query(Team).join(user_teams).filter(
        user_teams.c.user_id == user_id).all()
    if not teams:
        return {"teams": [], "message": "No teams found for this user"}

    return {"teams": [{"id": team.id, "name": team.name} for team in teams]}


@router.post("/api/event/{event_id}/teams/join", summary="User Join Team", tags=["Event", "Team"])
def join_team(event_id: int, request: JoinTeamRequest):
    """
    Dispatch a task to allow a user to join a team in a specific event.
    """
    async_result = join_team_task.delay(
        event_id, request.user_id, request.team_id)
    return {"message": "Join team initiated", "task_id": async_result.id}


@router.get("/api/team/{team_id}/members", summary="Get Team Members", tags=["Team"])
def get_team_members(team_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Retrieve all members of a specific team using the user_teams association table.
    """
    # Query for users who are members of the specified team
    users = db.query(User).join(user_teams, User.id == user_teams.c.user_id).filter(
        user_teams.c.team_id == team_id
    ).all()

    # If no members are found, raise an HTTPException
    if not users:
        raise HTTPException(
            status_code=404, detail="No members found for this team")

    # Return a list of usernames for the team members
    return {"members": [user.username for user in users]}


# ------------------ Score Routes ------------------


@router.get("/api/event/{event_id}/ranking", summary="Get Event Rankings", tags=["Event", "Ranking"])
def get_event_ranking(event_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Retrieve ranking information for an event and calculate scores asynchronously.
    """
    teams = db.query(Team.id).filter(Team.event_id == event_id).all()
    team_ids = [team.id for team in teams]

    # Dispatch score calculation tasks
    async_results = [calculate_team_score_task.delay(
        team_id) for team_id in team_ids]
    return {"message": "Ranking calculation initiated", "tasks": [result.id for result in async_results]}


@router.get("/api/team/{team_id}/score", summary="Get Team Score", tags=["Team", "Score"])
def get_team_score(team_id: int):
    """
    Retrieve the team's score. Check Redis cache first; if not available, calculate it asynchronously.
    """
    from database import get_redis_connection
    redis_conn = get_redis_connection()
    score = redis_conn.get(f"team:{team_id}:score")

    if score is not None:
        return {"team_id": team_id, "score": float(score)}

    # If not cached, calculate asynchronously
    async_result = calculate_team_score_task.delay(team_id)
    return {"message": "Score calculation initiated", "task_id": async_result.id}


@router.post("/api/score/update", summary="Batch Update Team Scores", tags=["Score"])
def update_scores(request: UpdateScoreRequest):
    """
    Dispatch a task to batch update team scores asynchronously.
    """
    # Validate the request data
    if not request.scores or not isinstance(request.scores, list):
        raise HTTPException(
            status_code=400, detail="Invalid scores data. It should be a list of team scores.")

    # Prepare the scores for the task
    scores = [{"team_id": score.team_id, "value": score.value}
              for score in request.scores]

    # Dispatch the Celery task
    async_result = persist_team_scores_task.delay(scores)

    return {"message": "Batch score update initiated", "task_id": async_result.id}
