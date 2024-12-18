from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Event, Team, User, Checkin, Score
from models.association import user_teams
from datetime import datetime
from database import get_postgresql_connection
from request.main import CreateEventRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
# from google.cloud import bigquery
from datetime import datetime
from database import get_postgresql_connection
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
import base64
import uuid
import os
from datetime import datetime, timedelta, timezone
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi import Query

from services.score_service import calculate_team_score

from models import (
    User,
    Team,
    Checkin,
    Score,
    Ranking,
    Event
)
from models.association import user_teams
import re
from google.cloud import storage
from request.main import (
    RegisterUserRequest,
    LoginRequest,
    CreateTeamRequest,
    UserCheckinRequest,
    UpdateScoreRequest,
    CreateEventRequest,
    JoinTeamRequest,
    UploadRequest
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter()


def upload_to_gcp(bucket_name: str, file_data: bytes, file_name: str):
    print("Uploading file to GCP Cloud Storage...")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(file_data, content_type="image/png")
    return f"https://storage.googleapis.com/{bucket_name}/{file_name}"

def is_event_active(event_id: int, db: Session):
    """
    檢查活動是否存在，並判斷是否在活動的時間範圍內。
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    current_time = datetime.now(timezone.utc)

    if current_time < event.start_time:
        raise HTTPException(status_code=400, detail="The event has not started yet")
    if current_time > event.end_time:
        raise HTTPException(status_code=400, detail="The event has already ended")

    return event

# ------------------ Event Routes ------------------


@router.post("/api/event/create", summary="Create Event", tags=["Event"], response_description="Event creation success")
def create_event(request: CreateEventRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Create a new event with start and end times.
    """
    # 計算 UTC+8 的當前時間
    utc_offset = timedelta(hours=8)
    current_time = datetime.now(timezone.utc) + utc_offset

    if request.start_time >= request.end_time:
        raise HTTPException(
            status_code=400, detail="Start time must be before end time"
        )

    new_event = Event(
        name=request.name,
        description=request.description,
        start_time=request.start_time,
        end_time=request.end_time,
        created_at=current_time  # 使用 UTC+8 時間
    )
    try:
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return {"message": "Event created successfully", "event_id": new_event.id}
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create event")
        
@router.post("/api/event/{event_id}/upload", summary="Upload Check-in Data", tags=["Event", "Upload"])
def upload_checkin(event_id: int, request: UploadRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Upload check-in data for all teams the user belongs to in a specific event.
    """
    event = is_event_active(event_id, db)

    # 1. 驗證活動是否存在
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. 查詢使用者所屬的所有隊伍 (在指定活動內)
    user_teams_query = db.query(Team).join(user_teams).filter(
        user_teams.c.user_id == request.user_id,  # 使用 user_id
        Team.event_id == event_id  # 確保隊伍屬於該活動
    ).all()
    print("User Teams:", user_teams_query)
    if not user_teams_query:
        raise HTTPException(
            status_code=404, detail="User does not belong to any teams in this event")

    # 3. 上傳照片到 GCP Cloud Storage
    photo_url = None
    if request.photo:
        try:
            bucket_name = os.environ.get("GCP_BUCKET_NAME")
            file_data = base64.b64decode(request.photo)
            file_name = f"checkin_photos/{uuid.uuid4()}.png"
            photo_url = upload_to_gcp(bucket_name, file_data, file_name)
            print("Photo URL:", photo_url)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload photo: {str(e)}")

    if not request.comment:
        request.comment = "zxc"

    # 4. Create check-in records for all teams
    created_checkins = []
    for team in user_teams_query:
        new_checkin = Checkin(
            user_id=request.user_id,  # Assign user_id here
            team_id=team.id,
            content=request.comment,
            created_at=request.created_at,
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
                "created_at": request.created_at
            })

            # 計算分數
            new_score = calculate_team_score(team.id, db)
            
            # 儲存新的分數到 PostgreSQL
            score_entry = db.query(Score).filter(Score.team_id == team.id).first()
            if score_entry:
                # 如果已有紀錄，則更新分數
                score_entry.score = new_score
                score_entry.updated_at = datetime.utcnow()
            else:
                # 如果沒有紀錄，則新增
                new_score_entry = Score(team_id=team.id, score=new_score)
                db.add(new_score_entry)

            db.commit()

        except Exception as e:
            print("Database Error:", str(e))
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Database insert failed: {str(e)}")

    return {
        "message": "Check-in data uploaded successfully for all teams",
        "checkins": created_checkins
    }


@router.get("/api/event/{event_id}/upload/list", summary="Get All Uploads for Event", tags=["Event", "Upload"])
def get_event_uploads(event_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Get all uploads (photos and comments) for a specific event.
    """
    # 驗證活動是否存在
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 查詢該活動所有上傳數據 (Checkin)
    uploads = (
        db.query(Checkin)
        .join(Team, Team.id == Checkin.team_id)
        .filter(Team.event_id == event_id)
        .all()
    )

    # 如果沒有任何上傳數據，返回空列表
    if not uploads:
        return {"uploads": []}

    # 返回格式化的上傳數據
    return {
        "uploads": [
            {
                "user_id": upload.user_id,
                "team_id": upload.team_id,
                "comment": upload.content,
                "photo_url": upload.photo_url,
                "created_at": upload.created_at,
            }
            for upload in uploads
        ]
    }


@router.get("/api/event/all", summary="Get All Events", tags=["Event"], response_description="List of all events")
def get_events(db: Session = Depends(get_postgresql_connection)):
    """
    Retrieve all events sorted by created_at in descending order with a limit.
    """
    # 按 created_at 降序排序，並限制返回數量
    events = (
        db.query(Event.id, Event.name, Event.start_time, Event.end_time, Event.created_at)
        .order_by(Event.created_at.desc())  # 按 created_at 降序排序
        .limit(10)  # 限制返回的筆數為 10
        .all()
    )

    # 格式化結果
    return {
        "events": [
            {
                "id": event.id,
                "name": event.name,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "created_at": event.created_at,  # 返回創建時間
            }
            for event in events
        ]
    }

@router.get("/api/event/{event_id}", summary="Get Event by ID", tags=["Event"], response_description="Details of a specific event")
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
        "description": event.description,  # 可以返回更多的字段
        "start_time": event.start_time,
        "end_time": event.end_time,
        "created_at": event.created_at,  # 返回創建時間
    }


@router.post("/api/event/{event_id}/checkin", summary="User Check-in for Event", tags=["Event", "Checkin"])
def user_checkin(event_id: int, request: UserCheckinRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Record a check-in for a user in a specific event.
    """
    # Find the event by event_id
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Find the user by user_id
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find the team by team_id
    team = db.query(Team).filter(Team.id == request.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Verify if the user is part of the team
    user_team = db.query(user_teams).filter(
        user_teams.c.user_id == request.user_id,
        user_teams.c.team_id == request.team_id
    ).first()
    if not user_team:
        raise HTTPException(
            status_code=403, detail="User does not belong to this team"
        )

    # Record the check-in for the user
    new_checkin = Checkin(
        user_id=request.user_id,
        team_id=request.team_id,
        content=request.content  # Content can be any additional check-in information
    )
    db.add(new_checkin)
    db.commit()
    db.refresh(new_checkin)

    # Return success message
    return {"message": "Check-in recorded successfully", "checkin_id": new_checkin.id}


# ------------------ Team Routes ------------------
@router.options("/{rest_of_path:path}")
async def preflight_check(rest_of_path: str):
    headers = {
        "Access-Control-Allow-Origin": "https://frontend-service-72785805306.asia-east1.run.app",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
    }
    return JSONResponse(content={}, headers=headers)
from datetime import datetime, timedelta, timezone

@router.post("/api/event/{event_id}/team/create", summary="Create Team for Event", tags=["Event", "Team"], response_description="Create team successfully")
def create_team(event_id: int, request: CreateTeamRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Create a new team for a specific event.
    """
    # 直接計算 UTC+8 時區的當前時間
    current_time = datetime.now(timezone.utc) + timedelta(hours=8)

    # 1. 查找活動
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. 驗證隊伍名稱是否重複
    existing_team = db.query(Team).filter(
        Team.name == request.name, Team.event_id == event_id
    ).first()
    if existing_team:
        raise HTTPException(
            status_code=400, detail="Team name already exists for this event"
        )

    # 3. 創建新隊伍
    new_team = Team(
        name=request.name,
        description=request.description,
        event_id=event_id,
        created_at=current_time  # 使用計算的 UTC+8 時間
    )

    try:
        db.add(new_team)
        db.commit()
        db.refresh(new_team)
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create team")

    # 返回成功訊息與隊伍 ID
    return {"message": "Team created successfully", "team_id": new_team.id}


@router.get("/api/event/{event_id}/teams", summary="Get Teams for an Event", tags=["Event"], response_description="活動的隊伍列表")
def get_teams_for_event(
    event_id: int,
    page: int = Query(1, ge=1),  # 默認第 1 頁
    page_size: int = Query(10, ge=1, le=100),  # 每頁大小，限制為 1-100
    db: Session = Depends(get_postgresql_connection)
):
    """
    Get all teams for a specific event with pagination.
    """
    # 查找該活動
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 計算偏移量
    offset = (page - 1) * page_size

    # 查詢隊伍數據，加入分頁
    teams = db.query(Team).filter(Team.event_id == event_id).offset(offset).limit(page_size).all()

    # 查詢總數量以供前端顯示分頁
    total_teams = db.query(Team).filter(Team.event_id == event_id).count()

    return {
        "total_teams": total_teams,
        "page": page,
        "page_size": page_size,
        "teams": [{"id": team.id, "name": team.name, "members": team.members} for team in teams]
    }

@router.get("/api/team/{team_id}/members", summary="Get Team Members", tags=["Team"], response_description="團隊成員列表")
def get_team_members(team_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Get all members of a specific team using the user_teams table.
    """
    users = db.query(User).join(user_teams, User.id == user_teams.c.user_id).filter(
        user_teams.c.team_id == team_id
    ).all()

    if not users:
        raise HTTPException(
            status_code=404, detail="No members found for this team")

    return {"members": [user.username for user in users]}


@router.post("/api/event/{event_id}/teams/join", summary="User Join Team", tags=["Event", "Team"])
def join_team(event_id: int, request: JoinTeamRequest, db: Session = Depends(get_postgresql_connection)):
    """
    User joins a team for a specific event.
    """
    event = is_event_active(event_id, db)

    # 1. 查找活動
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. 查找隊伍
    team = db.query(Team).filter(Team.id == request.team_id).first()
    if not team or team.event_id != event_id:
        raise HTTPException(
            status_code=404, detail="Team not found or not associated with this event"
        )

    # 3. 查找使用者
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 4. 檢查使用者是否已經在隊伍中
    existing_user_team = db.query(user_teams).filter(
        user_teams.c.user_id == request.user_id,
        user_teams.c.team_id == request.team_id
    ).first()

    if existing_user_team:
        raise HTTPException(
            status_code=400, detail="User already in this team"
        )

    # 5. 插入使用者與隊伍的關聯資料
    try:
        insert_statement = user_teams.insert().values(
            user_id=request.user_id,
            team_id=request.team_id
        )
        print(f"Executing SQL: {insert_statement}")  # 調試用
        db.execute(insert_statement)  # 插入資料到 user_teams 表
        db.commit()  # 提交資料庫更改

        print(f"User {request.user_id} successfully joined Team {request.team_id}")

    except Exception as e:
        print(f"Database Error: {str(e)}")  # 調試用
        db.rollback()  # 回滾資料庫變更
        raise HTTPException(
            status_code=500, detail=f"Database insert failed: {str(e)}"
        )

    return {"message": "User successfully joined the team for the event"}

@router.get("/api/event/{event_id}/ranking", summary="Get Event Rankings", tags=["Event", "Ranking"])
def get_event_ranking(event_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Retrieve ranking information for an event, including scores and team sizes.
    """
    # 驗證活動是否存在
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=400, detail="Event not found")

    # 查詢活動中的最高分的20個隊伍
    top_teams = db.query(Team).join(Score).filter(Team.event_id == event_id).order_by(Score.score.desc()).limit(20).all()
    if not top_teams:
        raise HTTPException(
            status_code=400, detail="No teams found for this event")

    # 構建排名數據
    rankings = []
    for team in top_teams:
        # 查詢隊伍的分數
        score = db.query(Score).filter(Score.team_id == team.id).first()
        team_score = score.score if score else 0.0  # 修正為正確的 score 屬性

        rankings.append({
            "team_id": team.id,
            "team_name": team.name,
            "score": team_score,
        })

    return {"rankings": rankings}