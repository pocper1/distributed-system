import re
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from database import get_postgresql_connection, get_redis_connection

from models import Event, Team, User, Checkin, Score, Ranking
from models.association import user_teams
from request.main import RegisterUserRequest, LoginRequest, CreateTeamRequest, UserCheckinRequest, UpdateScoreRequest, CreateEventRequest, JoinTeamRequest, UploadRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
utc_plus_8 = timezone(timedelta(hours=8))

router = APIRouter()

# ------------------ Health Check ------------------

@router.get("/healthz", summary="Health Check", tags=["System"], description="API 健康檢查")
def read_root():
    """
    Health check endpoint.
    """
    return {"message": "API is running successfully"}

@router.get("/api/redis/ping", summary="Test Redis Connection", tags=["System"])
def test_redis_connection():
    """
    Test connection to Redis by sending a PING command.
    """
    try:
        redis_conn = get_redis_connection()
        pong = redis_conn.ping()
        return {"message": "Redis connection successful", "response": "PONG" if pong else "No response"}
    except Exception as e:
        return {"message": "Redis connection failed", "error": str(e)}


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
        "created_at": user.created_at.astimezone(utc_plus_8).isoformat(),
    }


# ------------------ Ranking Routes ------------------

@router.post("/admin/reset-db")
async def reset_db():
    await database.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    return {"message": "Database reset successfully"}