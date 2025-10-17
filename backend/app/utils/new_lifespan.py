"""
Lifespan context manager for MongoDB connection
"""
from contextlib import asynccontextmanager
from app.database.mongo_db import connect_to_mongo, close_mongo_connection
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app):
    """
    Lifespan context manager for FastAPI app
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting up application...")
    await connect_to_mongo()
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_mongo_connection()
    logger.info("Application shutdown complete")
