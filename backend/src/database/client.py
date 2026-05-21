from databases import Database
from log import logger

from .config import database_settings

db = Database(database_settings.DB_URL, min_size=5, max_size=20)


async def connect_db():
    try:
        logger.info("Connecting to database")
        await db.connect()
        logger.success("Database connected successfully")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise e


async def disconnect_db():
    try:
        logger.info("Disconnecting from database")
        await db.disconnect()
        logger.success("Database disconnected successfully")
    except Exception as e:
        logger.error(f"Error disconnecting from database: {e}")
        raise e


def get_pool_stats():
    try:
        stats = {
            "size": db.size,
            "min_size": db.min_size,
            "max_size": db.max_size,
            "free": len(db.free_cons),
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting database pool stats: {e}")
        return {}
