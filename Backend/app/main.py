
from fastapi import FastAPI
import logging
import threading
from services.score_updater import subscribe_and_sync_scores, startup_sync_scores

# custom
from routes.main import router
from database import get_postgresql_connection, get_redis_connection
from models import *


# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set log level to INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Log to standard output
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Marketing Campaign API",
    description="This API manages user registration, events, teams, check-ins, and rankings.",
    version="1.0.0",
)

# Initialize PostgreSQL connection
try:
    logger.info("Connecting to PostgreSQL...")
    postgres_conn = get_postgresql_connection()
    logger.info("PostgreSQL connection established.")
except Exception as e:
    logger.error(f"Failed to connect to PostgreSQL: {e}")

# Initialize Redis connection
try:
    logger.info("Connecting to Redis...")
    redis_conn = get_redis_connection()
    logger.info("Redis connection established.")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")

# Include all routes from /app/routes/main.py
app.include_router(router)

def start_sync_thread():
    """
    啟動 Redis Pub/Sub 監聽器線程
    """
    threading.Thread(target=subscribe_and_sync_scores, daemon=True).start()
    print("Started Redis Pub/Sub listener thread.")

@app.on_event("startup")
def on_startup():
    startup_sync_scores()

# Start the score updater thread
start_sync_thread()
