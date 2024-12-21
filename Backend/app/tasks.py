import os
import re
import uuid
import base64
import aiofiles
from datetime import datetime, timezone, timedelta

from passlib.context import CryptContext
from google.cloud import storage

from models import Event, Checkin, Team, User, Score, Ranking
from models.association import user_teams
from database import celery_app, get_postgresql_connection, get_synchronous_session
from sqlalchemy.exc import SQLAlchemyError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.create_checkin_records_task")
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


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.upload_to_gcp_task")
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


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.create_team_task")
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


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.get_teams_task")
def get_teams_task(self, event_id):
    """
    Background task to get all teams for a specific event.
    """
    try:
        db_gen = get_postgresql_connection()
        db = next(db_gen)

        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")

        teams = db.query(Team).filter(Team.event_id == event_id).all()

        return [{"id": team.id, "name": team.name, "members": team.members} for team in teams]
    except Exception as exc:
        self.retry(exc=exc)
    finally:
        db.close()



@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.join_team_task")
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

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10, name="tasks.register_user_task")
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


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10, name="tasks.calculate_team_score_task")
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


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.persist_team_scores_task")
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


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.get_user_teams_task")
def get_user_teams_task(self, user_id):
    """
    Background task to get all teams a user has joined.
    """
    try:
        db_gen = get_postgresql_connection()
        db = next(db_gen)

        teams = db.query(Team).join(user_teams).filter(
            user_teams.c.user_id == user_id
        ).all()

        if not teams:
            return {"teams": [], "message": "No teams found for this user"}

        return [{"id": team.id, "name": team.name} for team in teams]
    except Exception as exc:
        self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.get_team_members_task")
def get_team_members_task(self, team_id):
    """
    Background task to retrieve all members of a specific team.
    """
    try:
        db_gen = get_postgresql_connection()
        db = next(db_gen)

        users = db.query(User).join(user_teams, User.id == user_teams.c.user_id).filter(
            user_teams.c.team_id == team_id
        ).all()

        if not users:
            raise ValueError("No members found for this team")

        return [{"id": user.id, "username": user.username} for user in users]
    except Exception as exc:
        self.retry(exc=exc)
    finally:
        db.close()
        
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.create_event_task")
def create_event_task(self, name: str, description: str, start_time: str, end_time: str):
    """
    Celery task to create a new event in the database.

    Args:
        name (str): Name of the event.
        description (str): Description of the event.
        start_time (str): Start time of the event in ISO format.
        end_time (str): End time of the event in ISO format.

    Returns:
        dict: Dictionary containing the event ID and success message, or error details.
    """
    # Obtain a synchronous session
    session_generator = get_synchronous_session()
    session = next(session_generator)

    try:
        # Convert ISO strings to datetime objects
        start_time_utc = datetime.fromisoformat(start_time).astimezone(timezone.utc).replace(tzinfo=None)
        end_time_utc = datetime.fromisoformat(end_time).astimezone(timezone.utc).replace(tzinfo=None)

        # Ensure start_time is before end_time
        if start_time_utc >= end_time_utc:
            raise ValueError("Start time must be before end time.")

        # Check for existing event with the same name
        existing_event = session.query(Event).filter_by(name=name).first()
        if existing_event:
            raise ValueError(f"An event with the name '{name}' already exists.")

        # Create new event
        new_event = Event(
            name=name,
            description=description,
            start_time=start_time_utc,
            end_time=end_time_utc,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        session.add(new_event)
        session.commit()

        return {"event_id": new_event.id, "message": "Event created successfully."}

    except (SQLAlchemyError, ValueError) as e:
        session.rollback()
        if isinstance(e, SQLAlchemyError):
            try:
                self.retry(exc=e)
            except self.MaxRetriesExceededError:
                return {"error": f"Database error: {str(e)}"}
        else:
            return {"error": str(e)}
    except Exception as e:
        session.rollback()
        return {"error": f"Unexpected error: {str(e)}"}
    finally:
        session.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.upload_checkin_data_task")
async def upload_checkin_data_task(event_id: int, user_id: int, comment: str, photo: str):
    """
    Celery task to handle photo upload and initiate check-in record creation.
    
    Args:
        event_id (int): ID of the event.
        user_id (int): ID of the user uploading the data.
        comment (str): Comment provided by the user.
        photo (str): Base64-encoded photo data.

    Returns:
        dict: Dictionary with the result message or error details.
    """
    db_gen = get_synchronous_session()
    db = next(db_gen)
    try:
        # Verify if the event exists
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return {"error": "Event not found."}

        # Decode photo if provided
        photo_url = None
        if photo:
            file_data = base64.b64decode(photo)
            file_name = f"checkin_photos/{uuid.uuid4()}.png"

            # Handle local or cloud upload
            env = os.getenv("ENV", "dev").lower()
            if env == "dev":
                tmp_path = f"/tmp/{file_name}"
                try:
                    async with aiofiles.open(tmp_path, "wb") as f:
                        await f.write(file_data)
                    photo_url = f"file://{tmp_path}"
                except Exception as e:
                    return {"error": f"Failed to save photo locally: {str(e)}"}
            else:
                # Dispatch GCP upload task
                bucket_name = os.getenv("GCP_BUCKET_NAME")
                if not bucket_name:
                    return {"error": "GCP_BUCKET_NAME not set."}

                upload_result = upload_to_gcp_task.apply_async(kwargs={
                    "bucket_name": bucket_name,
                    "file_data": file_data,
                    "file_name": file_name
                })
                photo_url = upload_result.get(timeout=300)

                if "Failed" in photo_url:
                    return {"error": f"Photo upload failed: {photo_url}"}

        # Dispatch check-in creation task
        create_checkin_records_task.delay(
            user_id=user_id,
            team_ids=[team.id for team in db.query(Team).filter(Team.event_id == event_id).all()],
            comment=comment,
            photo_url=photo_url
        )
        return {"message": "Photo upload and check-in initiation completed."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.create_checkin_records_task")
def create_checkin_records_task(user_id: int, team_ids: list, comment: str, photo_url: str):
    """
    Celery task to create check-in records for multiple teams.
    
    Args:
        user_id (int): ID of the user.
        team_ids (list): List of team IDs.
        comment (str): Comment provided by the user.
        photo_url (str): URL of the uploaded photo.

    Returns:
        dict: Dictionary with success message or error details.
    """
    db_gen = get_synchronous_session()
    db = next(db_gen)
    try:
        for team_id in team_ids:
            checkin = Checkin(
                user_id=user_id,
                team_id=team_id,
                content=comment,
                photo_url=photo_url,
                created_at=datetime.now(timezone.utc)
            )
            db.add(checkin)
        db.commit()
        return {"message": "Check-in records created successfully."}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="tasks.fetch_event_uploads_task")
def fetch_event_uploads_task(event_id: int):
    """
    Celery task to fetch all uploads for a specific event.
    
    Args:
        event_id (int): ID of the event.

    Returns:
        list: List of dictionaries containing upload details or error details.
    """
    db_gen = get_synchronous_session()
    db = next(db_gen)
    try:
        uploads = (
            db.query(Checkin)
            .join(Team, Team.id == Checkin.team_id)
            .filter(Team.event_id == event_id)
            .all()
        )
        return [
            {
                "user_id": upload.user_id,
                "team_id": upload.team_id,
                "comment": upload.content,
                "photo_url": upload.photo_url,
                "created_at": upload.created_at.isoformat(),
            }
            for upload in uploads
        ]
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()