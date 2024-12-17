from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
# from google.cloud import bigquery
from datetime import datetime
from database import get_postgresql_connection
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

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

from request.main import (
    RegisterUserRequest,
    LoginRequest,
    CreateTeamRequest,
    UserCheckinRequest,
    UpdateScoreRequest,
    CreateEventRequest
)

# 初始化密碼加密器
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 初始化 BigQuery 客戶端
# bq_client = bigquery.Client()

router = APIRouter()

# ------------------ Health Check ------------------
@router.get("/healthz", summary="Health Check", tags=["System"], description="API 健康檢查")
def read_root():
    """
    Health check endpoint.
    """
    return {"message": "API is running successfully"}


# ------------------ User Routes ------------------

@router.post("/api/user/register", summary="Register User", tags=["User"], response_description="註冊成功訊息")
def register_user(request: RegisterUserRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Register a new user.
    """
    # 驗證 email 格式
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, request.email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    # 檢查 email 是否已經被註冊
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 加密密碼
    hashed_password = pwd_context.hash(request.password)

    # 創建新用戶
    new_user = User(
        username=request.username,
        email=request.email,
        password=hashed_password  # 儲存加密後的密碼
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.post("/api/user/login", summary="User Login")
def login_user(request: LoginRequest, db: Session = Depends(get_postgresql_connection)):
    """
    User login: Verify email and password, then return success message only.
    """
    # 驗證用戶
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # 返回用戶的 username
    return {"message": "Login successful", "username": user.username}

# ------------------ Team Routes ------------------
@router.post("/api/team/create", summary="Create Team", tags=["Team"], response_description="團隊創建成功")
def create_team(request: CreateTeamRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Create a new team.
    """
    existing_team = db.query(Team).filter(Team.name == request.name).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Team name already exists")
    new_team = Team(name=request.name, description=request.description)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return {"message": "Team created successfully", "team_id": new_team.id}


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


# ------------------ Event Routes ------------------
@router.post("/api/event/create", summary="Create Event", tags=["Event"], response_description="活動創建成功")
def create_event(request: CreateEventRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Create a new event with start and end times.
    """
    if request.start_time >= request.end_time:
        raise HTTPException(
            status_code=400, detail="Start time must be before end time")

    new_event = Event(
        name=request.name,
        description=request.description,
        start_time=request.start_time,
        end_time=request.end_time
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return {"message": "Event created successfully", "event_id": new_event.id}


@router.get("/api/event/all", summary="Get All Events", tags=["Event"], response_description="活動列表")
def get_events(db: Session = Depends(get_postgresql_connection)):
    """
    Retrieve all events.
    """
    events = db.query(Event).all()
    return {"events": [{"id": e.id, "name": e.name, "start_time": e.start_time, "end_time": e.end_time} for e in events]}


# ------------------ Check-in Routes ------------------
@router.post("/api/checkin")
def user_checkin(request: UserCheckinRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Record a check-in for a user.
    """
    # Check if the user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the team exists
    team = db.query(Team).filter(Team.id == request.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Verify user-team relationship
    user_team = db.query(user_teams).filter(
        user_teams.c.user_id == request.user_id,
        user_teams.c.team_id == request.team_id
    ).first()
    if not user_team:
        raise HTTPException(
            status_code=403, detail="User does not belong to this team")

    # Record check-in
    new_checkin = Checkin(
        user_id=request.user_id,
        team_id=request.team_id,
        content=request.content
    )
    db.add(new_checkin)
    db.commit()
    db.refresh(new_checkin)
    return {"message": "Check-in recorded successfully", "checkin_id": new_checkin.id}


# ------------------ Score Routes ------------------
@router.post("/api/score/update")
def update_score(request: UpdateScoreRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Update a team's score.
    """
    team = db.query(Team).filter(Team.id == request.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    score_entry = db.query(Score).filter(
        Score.team_id == request.team_id).first()
    if score_entry:
        score_entry.score = request.value
        score_entry.updated_at = datetime.utcnow()
    else:
        new_score = Score(team_id=request.team_id, score=request.value)
        db.add(new_score)

    db.commit()
    return {"message": "Score updated successfully", "team_id": request.team_id, "score": request.value}


# ------------------ Ranking Routes ------------------

# @router.get("/api/ranking", summary="Get Team Rankings", tags=["Ranking"], response_description="團隊排名列表")
# def get_ranking(db: Session = Depends(get_postgresql_connection)):
#     """
#     Retrieve team rankings from BigQuery.
#     """
#     try:
#         # BigQuery SQL 查詢語句，根據您的 BigQuery 表格結構修改
#         query = """
#         SELECT team_id, SUM(score) AS total_score
#         FROM `your_project_id.your_dataset.scores`
#         GROUP BY team_id
#         ORDER BY total_score DESC
#         LIMIT 20
#         """
#         query_job = bq_client.query(query)  # 執行查詢
#         results = query_job.result()

#         # 將查詢結果轉換成 JSON 格式
#         rankings = [
#             {"team_id": row.team_id, "total_score": row.total_score}
#             for row in results
#         ]
#         return {"rankings": rankings}
#     except Exception as e:
#         raise HTTPException(
#             status_code=404, detail="BigQuery table or dataset not found.")
