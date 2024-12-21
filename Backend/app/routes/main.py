import re
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from database import get_postgresql_connection, get_redis_connection

from models import Event, Team, User, Checkin, Score, Ranking
from models.association import user_teams
from request.main import (
    RegisterUserRequest,
    LoginRequest,
    CreateTeamRequest,
    UserCheckinRequest,
    UpdateScoreRequest,
    CreateEventRequest,
    JoinTeamRequest,
    UploadRequest,
)
from tasks import register_user_task, create_checkin_records_task

# 加密設定與時區
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
utc_plus_8 = timezone(timedelta(hours=8))

# 定義 API 路由
router = APIRouter()

# ------------------ System Routes ------------------

@router.get("/healthz", summary="Health Check", tags=["System"], description="API 健康檢查")
def health_check():
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


@router.post("/api/user/register", summary="Register User", tags=["User"])
def register_user(request: RegisterUserRequest):
    """
    Dispatch a task to register a new user.
    """
    # Dispatch the task to the Celery worker
    async_result = register_user_task.delay(request.username, request.email, request.password)
    
    # Return task ID to track the status
    return {"message": "User registration initiated", "task_id": async_result.id}


@router.post("/api/user/login", summary="User Login", tags=["User"])
def login_user(request: LoginRequest, db: Session = Depends(get_postgresql_connection)):
    """
    User login: Verify email and password, then return success message only.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "username": user.username,
        "is_superadmin": user.is_superadmin,
        "user_id": user.id,
        "is_login": True,
    }


@router.post("/api/user/logout", summary="User Logout", tags=["User"])
async def logout():
    """
    Notify the frontend to clear localStorage during logout.
    """
    return {"message": "Logout successful"}

@router.get("/api/user/{user_id}/info", summary="Get User Info", tags=["User"])
def get_user_info(user_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Get information of a specific user by user_id.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user.username,
        "email": user.email,
        "is_superadmin": user.is_superadmin,
        "created_at": user.created_at.astimezone(utc_plus_8).isoformat(),
    }

