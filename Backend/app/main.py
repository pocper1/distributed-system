
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
from fastapi.responses import JSONResponse

origins = os.getenv("ORIGINS", "")
origins_list = origins.split(",") if origins else []
print("Allowed Origins:", origins_list)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set log level to INFO
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
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

# Initialize PostgreSQL connection
try:
    logger.info("Connecting to PostgreSQL...")
    postgres_conn = get_postgresql_connection()
    logger.info("PostgreSQL connection established.")
except Exception as e:
    logger.error(f"Failed to connect to PostgreSQL: {e}")

app.include_router(router)
app.include_router(event_router)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('BACKEND_PORT', 8080)))