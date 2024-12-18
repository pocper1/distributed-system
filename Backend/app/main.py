
from fastapi import FastAPI
import logging
import uvicorn
import os

# custom
from routes.main import router
from routes.event import router as event_router

from database import get_postgresql_connection
from models import *
from fastapi.middleware.cors import CORSMiddleware

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
    title="按讚活動",
    description="按讚拿獎金",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-service-72785805306.asia-east1.run.app"], 
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 Headers
)


# Initialize PostgreSQL connection
try:
    logger.info("Connecting to PostgreSQL...")
    postgres_conn = get_postgresql_connection()
    logger.info("PostgreSQL connection established.")
except Exception as e:
    logger.error(f"Failed to connect to PostgreSQL: {e}")

# Include all routes from /app/routes/main.py
app.include_router(router)
app.include_router(event_router)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))