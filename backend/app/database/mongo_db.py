"""
MongoDB connection module using Motor (async MongoDB driver)
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.env import MONGO_URI, MONGO_DB_NAME
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Global MongoDB client and database instances
mongo_client: AsyncIOMotorClient = None
mongo_db = None


async def connect_to_mongo():
    """
    Connect to MongoDB database
    """
    global mongo_client, mongo_db
    try:
        mongo_client = AsyncIOMotorClient(MONGO_URI)
        mongo_db = mongo_client[MONGO_DB_NAME]

        # Test the connection
        await mongo_client.admin.command("ping")
        logger.info(f"Successfully connected to MongoDB: {MONGO_DB_NAME}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_mongo_connection():
    """
    Close MongoDB connection
    """
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """
    Get MongoDB database instance
    """
    return mongo_db


def get_collection(collection_name: str):
    """
    Get a specific collection from the database

    Args:
        collection_name: Name of the collection

    Returns:
        Collection instance
    """
    return mongo_db[collection_name]
