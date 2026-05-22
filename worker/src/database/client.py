from databases import Database
from loguru import logger

from config import general_settings

db = Database(general_settings.POSTGRES_URL, min_size=2, max_size=10)


async def connect_db():
    try:
        logger.info("Connecting to database")
        await db.connect()
        logger.success("Database connected successfully")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise


async def disconnect_db():
    try:
        logger.info("Disconnecting from database")
        await db.disconnect()
        logger.success("Database disconnected successfully")
    except Exception as e:
        logger.error(f"Error disconnecting from database: {e}")
        raise
