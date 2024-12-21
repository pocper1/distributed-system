# tasks.py

from database import celery_app, get_postgresql_connection
from sqlalchemy.orm import Session
from models import Checkin
from datetime import datetime, timezone, timedelta
from google.cloud import storage
import os
from models import Event, Team, User, Checkin, Score, Ranking
from models.association import user_teams

from database import celery_app, get_postgresql_connection
from sqlalchemy.orm import Session
from models import User
from passlib.context import CryptContext
import re
from database import celery_app, get_postgresql_connection
from sqlalchemy.orm import Session
from models import Checkin, Score, Team, user_teams
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
import aiofiles
import re


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def create_checkin_records_task(self, user_id: int, team_ids: list, comment: str, photo_url: str):
    """
    Background task to create check-in records for multiple teams.
    """
    try:
        # Obtain a new database session
        db_gen = get_postgresql_connection()
        db = next(db_gen)

        current_time = datetime.now(timezone.utc)
        checkins = []

        # Create Checkin instances for each team
        for team_id in team_ids:
            checkin = Checkin(
                user_id=user_id,
                team_id=team_id,
                content=comment,
                created_at=current_time,
                photo_url=photo_url
            )
            db.add(checkin)
            checkins.append(checkin)

        # Commit all check-ins at once for efficiency
        db.commit()

        # Refresh to get updated fields like `id`
        for checkin in checkins:
            db.refresh(checkin)

        # Prepare the response data
        created_checkins = [{
            "team_id": checkin.team_id,
            "checkin_id": checkin.id,
            "photo_url": checkin.photo_url,
            "created_at": checkin.created_at.astimezone(timezone(timedelta(hours=8))).isoformat(),
        } for checkin in checkins]

        return created_checkins

    except Exception as exc:
        # Retry the task in case of failure
        self.retry(exc=exc)
    finally:
        # Ensure the database session is closed
        db.close()


@celery_app.task(name="tasks.upload_to_gcp_task")
def upload_to_gcp_task(bucket_name: str, file_data: bytes, file_name: str) -> str:
    """
    Asynchronously upload a file to GCP Cloud Storage and return its URL.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(file_data, content_type="image/png")
        return f"https://storage.googleapis.com/{bucket_name}/{file_name}"
    except Exception as e:
        # Log the exception or handle accordingly
        return f"Failed to upload {file_name}: {str(e)}"


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def create_team_task(self, event_id: int, name: str, description: str):
    """
    Background task to create a team for an event.
    """
    try:
        db_gen = get_postgresql_connection()
        db = next(db_gen)

        current_time = datetime.now(timezone.utc)
        new_team = Team(
            name=name,
            description=description,
            event_id=event_id,
            created_at=current_time
        )
        db.add(new_team)
        db.commit()
        db.refresh(new_team)

        return {"message": "Team created successfully", "team_id": new_team.id}
    except Exception as exc:
        self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def join_team_task(self, event_id: int, user_id: int, team_id: int):
    """
    Background task to allow a user to join a team.
    """
    try:
        db_gen = get_postgresql_connection()
        db = next(db_gen)

        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")
        team = db.query(Team).filter(Team.id == team_id,
                                     Team.event_id == event_id).first()
        if not team:
            raise ValueError(
                "Team not found or not associated with this event")
        user_team = db.query(user_teams).filter(
            user_teams.c.user_id == user_id,
            user_teams.c.team_id == team_id
        ).first()
        if user_team:
            raise ValueError("User already in this team")

        insert_statement = user_teams.insert().values(
            user_id=user_id,
            team_id=team_id
        )
        db.execute(insert_statement)
        db.commit()

        return {"message": "User successfully joined the team"}
    except Exception as exc:
        self.retry(exc=exc)
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def register_user_task(self, username: str, email: str, password: str):
    """
    Asynchronous task to register a new user.
    """
    try:
        db_gen = get_postgresql_connection()
        db = next(db_gen)

        # Validate email format
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")

        # Check if the email is already registered
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("Email already registered")

        # Hash the password and create a new user
        hashed_password = pwd_context.hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "User registered successfully", "user_id": new_user.id}

    except Exception as exc:
        self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def calculate_team_score_task(self, team_id: int) -> float:
    """
    Asynchronous task to calculate and cache the team score.
    """
    try:
        # 計算分數
        from services.score_service import calculate_team_score
        score = calculate_team_score(team_id)
        
        # 快取到 Redis
        from database import get_redis_connection
        redis_conn = get_redis_connection()
        redis_conn.set(f"team:{team_id}:score", score, ex=3600)  # Cache for 1 hour

        return score
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def persist_team_scores_task(self, scores: list):
    """
    Batch persist multiple team scores to the database.
    """
    try:
        db_gen = get_postgresql_connection()
        db = next(db_gen)
        for team_id, score in scores:
            score_entry = db.query(Score).filter(Score.team_id == team_id).first()
            if score_entry:
                score_entry.score = score
                score_entry.updated_at = datetime.utcnow()
            else:
                new_score = Score(team_id=team_id, score=score)
                db.add(new_score)
        db.commit()
    except Exception as exc:
        self.retry(exc=exc)
    finally:
        db.close()