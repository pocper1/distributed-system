import os
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import text
from database import get_postgresql_connection, get_redis_connection, celery_app
from models import Event, Team
from models.association import user_teams
from sqlalchemy.sql import text
from celery.result import AsyncResult
from request.main import (
    CreateEventRequest,
    UploadRequest,
    UserCheckinRequest,
    CreateTeamRequest,
    JoinTeamRequest,
    UpdateScoreRequest
)
from redis import Redis
from tasks import (
    create_checkin_records_task, 
    create_team_task, 
    join_team_task, 
    calculate_team_score_task, 
    persist_team_scores_task, 
    create_event_task, 
    fetch_event_uploads_task, 
    upload_checkin_data_task
)

# Define router
router = APIRouter()

# Global settings
utc_plus_8 = timezone(timedelta(hours=8))
redis_conn: Redis = get_redis_connection()


# ------------------ Utility Functions ------------------

async def is_event_active(event_id: int, db: AsyncSession):
    """
    Check if the event is currently active (ongoing).
    """
    result = await db.execute(text("SELECT * FROM events WHERE id = :id", {"id": event_id}))
    event = result.fetchone()
    if not event:
        raise ValueError("Event not found")
    current_time = datetime.now(timezone.utc)
    return event.start_time <= current_time <= event.end_time


# ------------------ Event Routes ------------------


@router.post("/api/event/create", summary="Create Event", tags=["Event"])
async def create_event(request: CreateEventRequest):
    """
    Create a new event.
    """
    # Convert times to ISO format with UTC timezone
    request.start_time = request.start_time.astimezone(timezone.utc).isoformat()
    request.end_time = request.end_time.astimezone(timezone.utc).isoformat()

    # Ensure start time is earlier than end time
    if request.start_time >= request.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    # Submit Celery task
    try:
        task = create_event_task.apply_async(
            kwargs={
                "name": request.name,
                "description": request.description,
                "start_time": request.start_time,
                "end_time": request.end_time,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate event creation: {str(e)}")

    return {"message": "Event creation initiated.", "task_id": task.id}

@router.post("/api/event/{event_id}/upload", summary="Upload Check-in Data", tags=["Event"])
async def upload_checkin(event_id: int, request: UploadRequest, db: AsyncSession = Depends(get_postgresql_connection)):
    """
    Upload check-in data for all teams a user belongs to in a specific event.
    """
    if not await is_event_active(event_id, db):
        raise HTTPException(status_code=404, detail="Event is not active or does not exist.")

    task = upload_checkin_data_task.apply_async(kwargs={
        "event_id": event_id,
        "user_id": request.user_id,
        "comment": request.comment,
        "photo": request.photo
    })

    return {"message": "Check-in data upload initiated successfully.", "task_id": task.id}

@router.get("/api/event/{event_id}/upload/list", summary="Get All Uploads for Event", tags=["Event"])
async def get_event_uploads(event_id: int, db: AsyncSession = Depends(get_postgresql_connection)):
    """
    Retrieve all uploads (photos and comments) for a specific event.
    """
    task = fetch_event_uploads_task.apply_async(kwargs={"event_id": event_id})
    return {"message": "Fetching uploads initiated.", "task_id": task.id}


@router.get("/api/event/all", summary="Get All Events", tags=["Event"])
async def get_events(db: AsyncSession = Depends(get_postgresql_connection)):
    """
    Retrieve all events sorted by created_at in descending order with a limit.
    """
    events = await db.execute(
        text("SELECT id, name, start_time, end_time, created_at FROM events ORDER BY created_at DESC LIMIT 10")
    )
    result = events.fetchall()
    return {"events": [dict(row) for row in result]}


@router.get("/api/event/{event_id}", summary="Get Event by ID", tags=["Event"])
async def get_event(event_id: int, db: AsyncSession = Depends(get_postgresql_connection)):
    """
    Retrieve a specific event by its ID.
    """
    result = await db.execute(text("SELECT * FROM events WHERE id = :id", {"id": event_id}))
    event = result.fetchone()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return dict(event)


@router.post("/api/event/{event_id}/checkin", summary="User Check-in for Event", tags=["Event", "Checkin"])
async def user_checkin(event_id: int, request: UserCheckinRequest, db: AsyncSession = Depends(get_postgresql_connection)):
    """
    Record a check-in for a user in a specific event.
    """
    event = await db.execute(text("SELECT * FROM events WHERE id = :id", {"id": event_id}))
    if not event.fetchone():
        raise HTTPException(status_code=404, detail="Event not found")

    task = create_checkin_records_task.apply_async(kwargs={
        "event_id": event_id,
        "user_id": request.user_id,
        "team_id": request.team_id,
        "content": request.content
    })

    return {"message": "Check-in initiated successfully.", "task_id": task.id}


# ------------------ Team Routes ------------------

@router.post("/api/event/{event_id}/team/create", summary="Create Team for Event", tags=["Event", "Team"])
def create_team(event_id: int, request: CreateTeamRequest):
    """
    Dispatch a task to create a new team for a specific event.
    """
    async_result = create_team_task.delay(
        event_id, request.name, request.description)
    return {"message": "Team creation initiated", "task_id": async_result.id}


@router.get("/api/user/{user_id}/teams", summary="Get User Teams", tags=["User"], response_description="使用者的隊伍列表")
def get_user_teams(user_id: int):
    """
    Get all teams the user has joined.
    """
    # 呼叫 Celery 任務
    task = celery_app.send_task("tasks.get_user_teams", args=[user_id])
    return {"task_id": task.id}


@router.get("/api/event/{event_id}/teams", summary="Get Teams for an Event", tags=["Event"], response_description="活動的隊伍列表")
def get_teams_for_event(event_id: int):
    """
    Get all teams for a specific event.
    """
    # 呼叫 Celery 任務
    task = celery_app.send_task("tasks.get_teams", args=[event_id])
    return {"task_id": task.id}


@router.post("/api/event/{event_id}/teams/join", summary="User Join Team", tags=["Event", "Team"])
def join_team(event_id: int, request: JoinTeamRequest):
    """
    Dispatch a task to allow a user to join a team in a specific event.
    """
    async_result = join_team_task.delay(
        event_id, request.user_id, request.team_id)
    return {"message": "Join team initiated", "task_id": async_result.id}

@router.get("/api/team/{team_id}/members", summary="Get Team Members", tags=["Team"], response_description="隊伍的成員列表")
def get_team_members(team_id: int):
    """
    Retrieve all members of a specific team using the user_teams association table.
    """
    # 呼叫 Celery 任務
    task = celery_app.send_task("tasks.get_team_members", args=[team_id])
    return {"task_id": task.id}

# ------------------ Score Routes ------------------


@router.get("/api/event/{event_id}/ranking", summary="Get Event Rankings", tags=["Event", "Ranking"])
async def get_event_ranking(event_id: int, db: AsyncSession = Depends(get_postgresql_connection)):
    """
    Retrieve ranking information for an event and calculate scores asynchronously.
    """
    teams = await db.execute(text("SELECT id FROM teams WHERE event_id = :event_id", {"event_id": event_id}))
    team_ids = [team.id for team in teams.fetchall()]

    # Dispatch score calculation tasks
    async_results = [calculate_team_score_task.delay(team_id) for team_id in team_ids]
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

@router.get("/api/event/status/{task_id}", summary="Get Event Creation Status", tags=["Event"])
async def get_event_status(task_id: str):
    """
    Check the status of a Celery task.
    """
    result = AsyncResult(task_id, app=celery_app)
    
    if result.state == "PENDING":
        return {"status": result.state, "message": "Task is pending."}
    elif result.state == "SUCCESS":
        return {"status": result.state, "result": result.result}
    elif result.state == "FAILURE":
        return {"status": result.state, "error": str(result.info)}
    else:
        return {"status": result.state, "message": "Task is in progress."}