import os
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from redis import Redis

# Load environment variables from .env file
load_dotenv()

# PostgreSQL Configuration
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres_01")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Function to create a Cloud SQL connection using Google Cloud SQL Connector
def getconn():
    """
    Create a Cloud SQL connection using Cloud SQL Connector.
    """
    connector = Connector()  # Initialize the Cloud SQL Connector
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,  # Cloud SQL connection string
        driver="pg8000",           # PostgreSQL driver for Cloud SQL
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        db=POSTGRES_DB,
        ip_type=IPTypes.PUBLIC  # Use PUBLIC for external access; PRIVATE for VPC
    )
    return conn

# SQLAlchemy Configuration
Base = declarative_base()
engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function for PostgreSQL session
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
# def get_redis_connection():
#     """
#     Initialize and return a Redis connection.
#     """
#     redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
#     return redis_conn


def get_redis_connection():
    """
    Initialize Redis connection.
    """
    try:
        redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        redis_conn.ping()  # 測試 Redis 連線
        print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        return redis_conn
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        raise
