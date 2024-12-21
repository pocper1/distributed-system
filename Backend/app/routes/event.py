import re
import os
import uuid
import base64
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_postgresql_connection, get_redis_connection
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
from fastapi import BackgroundTasks
from redis import Redis
import shutil
from fastapi import UploadFile
from google.cloud import storage
from celery import Celery

redis_host = os.getenv("ORIGINS", "")

# Global settings
utc_plus_8 = timezone(timedelta(hours=8))
redis_conn = get_redis_connection()


# Define router
router = APIRouter()

# ------------------ Utility Functions ------------------
def upload_to_gcp(bucket_name: str, file_data: bytes, file_name: str):
    """
    Upload a file to GCP Cloud Storage and return its URL.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(file_data, content_type="image/png")
    return f"https://storage.googleapis.com/{bucket_name}/{file_name}"

def is_event_active(event_id: int, db: Session):
    """
    Check if the event is currently active (ongoing).
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise ValueError("Event not found")
    current_time = datetime.now(timezone.utc)
    return event.start_time <= current_time <= event.end_time

def get_team_score_from_cache(team_id: int):
    """
    Retrieve the team's score from Redis. If not available, calculate and cache it.
    """
    score = redis_conn.get(f"team:{team_id}:score")
    if score is not None:
        return float(score)

    # If not in Redis, calculate score from the database
    score = calculate_team_score(team_id)
    redis_conn.set(f"team:{team_id}:score", score, ex=3600)  # Cache score for 1 hour
    return score

def update_team_score_in_cache(team_id: int, new_score: float):
    """
    Update the team's score in Redis and enqueue a task to persist it to the database.
    """
    redis_conn.set(f"team:{team_id}:score", new_score, ex=3600)  # Update Redis
    return new_score

# ------------------ Event Routes ------------------

@router.post("/api/event/create", summary="Create Event", tags=["Event"])
def create_event(request: CreateEventRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Create a new event.
    """
    if request.start_time >= request.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")
    
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
        is_event_active(event_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Query all teams the user belongs to for the specific event
    user_teams_query = db.query(Team).join(user_teams).filter(
        user_teams.c.user_id == request.user_id,
        Team.event_id == event_id
    ).all()

    if not user_teams_query:
        raise HTTPException(
            status_code=404,
            detail="The user does not belong to any teams in this event."
        )

    # Upload photo to GCP Cloud Storage
    photo_url = None
    if request.photo:
        try:
            bucket_name = os.environ.get("GCP_BUCKET_NAME")
            if not bucket_name:
                raise EnvironmentError("GCP_BUCKET_NAME environment variable is not set.")
            
            file_data = base64.b64decode(request.photo)
            file_name = f"checkin_photos/{uuid.uuid4()}.png"
            photo_url = upload_to_gcp(bucket_name, file_data, file_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")

    # Create check-in records
    created_checkins = []
    for team in user_teams_query:
        new_checkin = Checkin(
            user_id=request.user_id,
            team_id=team.id,
            content=request.comment,
            created_at=datetime.now(timezone.utc),
            photo_url=photo_url
        )
        try:
            db.add(new_checkin)
            db.commit()
            db.refresh(new_checkin)

            created_checkins.append({
                "team_id": team.id,
                "checkin_id": new_checkin.id,
                "photo_url": photo_url,
                "created_at": new_checkin.created_at.astimezone(utc_plus_8).isoformat(),
            })

            # Calculate and update team score
            new_score = calculate_team_score(team.id, db)
            score_entry = db.query(Score).filter(Score.team_id == team.id).first()
            if score_entry:
                score_entry.score = new_score
                score_entry.updated_at = datetime.utcnow()
            else:
                new_score_entry = Score(team_id=team.id, score=new_score)
                db.add(new_score_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "message": "Check-in data uploaded successfully",
        "checkins": created_checkins
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
        db.query(Event.id, Event.name, Event.start_time, Event.end_time, Event.created_at)
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
        raise HTTPException(status_code=403, detail="User does not belong to this team")
    
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
def create_team(event_id: int, request: CreateTeamRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Create a new team for a specific event.
    """
    current_time = datetime.now(timezone.utc)
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    existing_team = db.query(Team).filter(
        Team.name == request.name, Team.event_id == event_id
    ).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Team name already exists for this event")
    
    new_team = Team(
        name=request.name,
        description=request.description,
        event_id=event_id,
        created_at=current_time
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return {"message": "Team created successfully", "team_id": new_team.id}

@router.get("/api/event/{event_id}/teams", summary="Get Teams for an Event", tags=["Event"])
def get_teams_for_event(
    event_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_postgresql_connection)
):
    """
    Get all teams for a specific event with pagination.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    offset = (page - 1) * page_size
    teams = db.query(Team).filter(Team.event_id == event_id).offset(offset).limit(page_size).all()
    total_teams = db.query(Team).filter(Team.event_id == event_id).count()
    return {
        "total_teams": total_teams,
        "page": page,
        "page_size": page_size,
        "teams": [{"id": team.id, "name": team.name} for team in teams]
    }

@router.post("/api/event/{event_id}/teams/join", summary="User Join Team", tags=["Event", "Team"])
def join_team(event_id: int, request: JoinTeamRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Allow a user to join a team in a specific event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    team = db.query(Team).filter(Team.id == request.team_id).first()
    if not team or team.event_id != event_id:
        raise HTTPException(status_code=404, detail="Team not found or not associated with this event")
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing_user_team = db.query(user_teams).filter(
        user_teams.c.user_id == request.user_id,
        user_teams.c.team_id == request.team_id
    ).first()
    if existing_user_team:
        raise HTTPException(status_code=400, detail="User already in this team")
    insert_statement = user_teams.insert().values(
        user_id=request.user_id,
        team_id=request.team_id
    )
    db.execute(insert_statement)
    db.commit()
    return {"message": "User successfully joined the team for the event"}

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
        raise HTTPException(status_code=404, detail="No members found for this team")

    # Return a list of usernames for the team members
    return {"members": [user.username for user in users]}


# ------------------ Score Routes ------------------


@router.get("/api/event/{event_id}/ranking", summary="Get Event Rankings", tags=["Event", "Ranking"])
def get_event_ranking(event_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Retrieve ranking information for an event, including scores and team sizes.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    rankings = (
        db.query(Team.id, Team.name, Score.score)
        .join(Score, Score.team_id == Team.id, isouter=True)
        .filter(Team.event_id == event_id)
        .order_by(Score.score.desc().nullslast())
        .limit(20)
        .all()
    )
    return {"rankings": [{"team_id": team_id, "team_name": team_name, "score": score or 0.0} for team_id, team_name, score in rankings]}

@router.post("/api/score/update", summary="Update Team Score", tags=["Score"])
def update_score(request: UpdateScoreRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_postgresql_connection)):
    """
    Update a team's score and persist the change in the database asynchronously.
    """
    new_score = request.value
    update_team_score_in_cache(request.team_id, new_score)

    # Add background task to update the database asynchronously
    background_tasks.add_task(persist_team_score_to_db, request.team_id, new_score, db)
    return {"message": "Score updated successfully", "team_id": request.team_id, "score": new_score}

def persist_team_score_to_db(team_id: int, score: float, db: Session):
    """
    Persist the team's score to the database.
    """
    score_entry = db.query(Score).filter(Score.team_id == team_id).first()
    if score_entry:
        score_entry.score = score
        score_entry.updated_at = datetime.utcnow()
    else:
        new_score_entry = Score(team_id=team_id, score=score)
        db.add(new_score_entry)
    db.commit()