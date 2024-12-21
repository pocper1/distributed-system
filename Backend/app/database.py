import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from redis import Redis
from celery import Celery
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

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

DATABASE_URL_ASYNC = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"  
DATABASE_URL_SYNC = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


# SQLAlchemy Configuration
Base = declarative_base()

# Synchronous Engine and Session
engine_sync = create_engine(
    DATABASE_URL_SYNC,
    echo=True,  # Set to False in production
)


engine_async: AsyncEngine = create_async_engine(
    DATABASE_URL_ASYNC,
    pool_size=20,        # Adjusted pool size
    max_overflow=10,     # Adjusted overflow
    pool_timeout=30,     # Reduced timeout
    pool_recycle=1800,   # Recycle connections every 30 minutes
    echo=True,           # Set to False in production
    future=True
)

SessionLocal = sessionmaker(
    bind=engine_async,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

SessionLocalSync = sessionmaker(
    bind=engine_sync,
    autoflush=False,
    autocommit=False,
)

# Celery Configuration
celery_app = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
)

# Celery optional configuration
celery_app.conf.update(
    result_expires=3600,  
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
celery_app.autodiscover_tasks(['tasks'])

# Asynchronous dependency for FastAPI
async def get_postgresql_connection() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# Synchronous dependency for Celery
def get_synchronous_session() -> Generator[Session, None, None]:
    session = SessionLocalSync()
    try:
        yield session
    finally:
        session.close()

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