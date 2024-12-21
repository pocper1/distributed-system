import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from redis import Redis
from celery import Celery

# Load environment variables from .env file
load_dotenv()

# Determine environment
env = os.getenv('ENV', 'dev').lower()

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST_LOCAL") if env == "dev" else os.getenv("POSTGRES_HOST_REMOTE")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST_LOCAL") if env == "dev" else os.getenv("REDIS_HOST_REMOTE")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))  # Default Redis DB

# SQLAlchemy Configuration
Base = declarative_base()

# Optimize PostgreSQL Connection Pool
# Reduced pool_size and max_overflow to prevent excessive connections to Cloud SQL
engine = sqlalchemy.create_engine(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
    pool_size=20,        # Adjusted pool size
    max_overflow=10,     # Adjusted overflow
    pool_timeout=30,     # Reduced timeout
    pool_recycle=1800,   # Recycle connections every 30 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Celery Configuration
celery_app = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    backend=f"db+postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Celery optional configuration
celery_app.conf.update(
    result_expires=3600,  
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Taipei",
    enable_utc=True,
)

# Dependency for PostgreSQL session
def get_postgresql_connection():
    """
    Yield a database session for FastAPI dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Redis Connection
def get_redis_connection():
    """
    Initialize Redis connection based on environment.
    """
    try:
        redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        redis_conn.ping()  # Test Redis connection
        print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}, DB: {REDIS_DB}")
        return redis_conn
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        raise

# Example: Test connections
if __name__ == "__main__":
    # Test PostgreSQL Connection
    print(f"Environment: {env}")
    print(f"Connecting to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}...")
    try:
        db = next(get_postgresql_connection())
        print("PostgreSQL connection successful!")
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")

    # Test Redis Connection
    try:
        redis = get_redis_connection()
        print("Redis connection successful!")
    except Exception as e:
        print(f"Redis connection failed: {e}")