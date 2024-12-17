from fastapi import APIRouter, Depends, HTTPException
from app.models.association import user_teams
from sqlalchemy.orm import Session
import redis
import os
from datetime import datetime

from app.database import get_postgresql_connection
from app.models import User, Team, Checkin, Score, Ranking
from app.requests.main import (
    RegisterUserRequest,
    LoginRequest,
    CreateTeamRequest,
    UserCheckinRequest,
    UpdateScoreRequest,
)

REDIS_IP = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

router = APIRouter()
cache = redis.StrictRedis(host=REDIS_IP, port=REDIS_PORT, decode_responses=True)

@router.get("/healthz")
def read_root():
    """
    Health check endpoint.
    """
    return {"message": "API is running successfully"}

# User routes
@router.post("/api/user/register")
def register_user(request: RegisterUserRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Register a new user.
    """
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(username=request.username, email=request.email, password=request.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.post("/api/user/login")
def login_user(request: LoginRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Log in a user by validating their credentials.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user or user.password != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id}

# Team routes
@router.post("/api/team/create")
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

@router.get("/api/team/{team_id}/members")
def get_team_members(team_id: int, db: Session = Depends(get_postgresql_connection)):
    """
    Get all members of a specific team using the user_teams table.
    """
    from app.models.user import User  # Import User model
    from app.models.team import Team  # Import Team model
    from app.models.user import user_teams  # Import user_teams table
    
    users = db.query(User).join(user_teams, User.id == user_teams.c.user_id).filter(
        user_teams.c.team_id == team_id
    ).all()

    if not users:
        raise HTTPException(status_code=404, detail="No members found for this team")

    return {"members": [user.username for user in users]}

# Check-in routes
@router.post("/api/checkin")
def user_checkin(request: UserCheckinRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Record a check-in for a user, only if the user belongs to the specified team.
    """
    # Check if the user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the team exists
    team = db.query(Team).filter(Team.id == request.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Verify that the user belongs to the team (check user_teams table)
    user_team = db.query(user_teams).filter(
        user_teams.c.user_id == request.user_id,
        user_teams.c.team_id == request.team_id
    ).first()
    if not user_team:
        raise HTTPException(
            status_code=403, 
            detail="User does not belong to this team"
        )

    # Proceed to record the check-in
    new_checkin = Checkin(
        user_id=request.user_id,
        team_id=request.team_id,
        content=request.content
    )
    db.add(new_checkin)
    db.commit()
    db.refresh(new_checkin)
    return {"message": "Check-in recorded successfully", "checkin_id": new_checkin.id}

# Score routes
@router.post("/api/score/update")
def update_score(request: UpdateScoreRequest, db: Session = Depends(get_postgresql_connection)):
    """
    Update a team's score.
    """
    # Check if the team exists
    team = db.query(Team).filter(Team.id == request.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Update or insert the score for the team
    score_entry = db.query(Score).filter(Score.team_id == request.team_id).first()
    if score_entry:
        score_entry.score = request.value
        score_entry.updated_at = datetime.utcnow()
    else:
        new_score = Score(team_id=request.team_id, score=request.value)
        db.add(new_score)
    
    db.commit()
    return {"message": "Score updated successfully", "team_id": request.team_id, "score": request.value}

# Ranking routes
@router.get("/api/ranking")
def get_ranking():
    """
    Retrieve dynamic ranking from Redis.
    """
    keys = cache.keys("team:*:score")
    scores = [(key.split(":")[1], float(cache.get(key))) for key in keys]
    rankings = sorted(scores, key=lambda x: x[1], reverse=True)
    return {"rankings": rankings}
