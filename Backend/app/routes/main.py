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
        raise HTTPException(
            status_code=401, detail="Invalid email or password")

    # 返回用戶的 username
    return {"message": "Login successful", "username": user.username, "is_superadmin": user.is_superadmin, "user_id": user.id, "is_login": True}

@router.post("/api/user/logout", summary="User Logout", tags=["User"])
async def logout():
    """
    登出功能，告訴前端清除 localStorage 中的資料
    """
    return {"message": "Logout successful"}

@router.get("/api/user/{user_id}/teams", summary="Get User Teams", tags=["User"])
def get_user_teams(user_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Get all teams the user has joined.
    """
    # 查找使用者所加入的所有隊伍
    teams = db.query(Team).join(user_teams).filter(user_teams.c.user_id == user_id).all()

    if not teams:
        return {"teams": [], "message": "No teams found for this user"}

    return {"teams": [{"id": team.id, "name": team.name} for team in teams]}

@router.get("/api/user/{user_id}/info", summary="Get User Info", tags=["User"])
def get_user_info(user_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Get information of a specific user by user_id.
    """
    # 查找用戶資料
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 返回用戶資料（可以根據需求調整返回的字段）
    return {
        "username": user.username,
        "email": user.email,
        "is_superadmin": user.is_superadmin,
        "created_at": user.created_at,
    }
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

