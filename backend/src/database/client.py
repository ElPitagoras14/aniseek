from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from log import logger

from .config import database_settings

# Translates the previous `databases` pool (min_size=5, max_size=20) into
# SQLAlchemy's model: `pool_size` permanent connections plus `max_overflow`
# temporary ones on top, so the total ceiling stays at 20 (design D7 of
# unify-database-access). The engine builds its pool lazily: no connection is
# opened until the first query runs.
engine: AsyncEngine = create_async_engine(
    database_settings.DB_URL,
    pool_size=5,
    max_overflow=15,
)


async def execute(conn: AsyncConnection, sql: str, params: dict | None = None) -> None:
    """Run a write query on the given connection."""
    await conn.execute(text(sql), params or {})


async def execute_many(conn: AsyncConnection, sql: str, params_list: list[dict]) -> None:
    """Run the same write query once per item in `params_list`, on the given connection."""
    await conn.execute(text(sql), params_list)


async def fetch_one(conn: AsyncConnection, sql: str, params: dict | None = None):
    """Return the first matching row as a dict-like mapping, or None."""
    result = await conn.execute(text(sql), params or {})
    return result.mappings().first()


async def fetch_all(conn: AsyncConnection, sql: str, params: dict | None = None):
    """Return all matching rows as dict-like mappings."""
    result = await conn.execute(text(sql), params or {})
    return result.mappings().all()


async def fetch_val(conn: AsyncConnection, sql: str, params: dict | None = None):
    """Return the first column of the first row, or None."""
    result = await conn.execute(text(sql), params or {})
    return result.scalar()


async def connect_db() -> None:
    """Verify connectivity at startup; fail loudly if the database doesn't respond."""
    try:
        logger.info("Connecting to database")
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.success("Database connected successfully")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise e


async def disconnect_db() -> None:
    """Release the engine's pool at shutdown."""
    try:
        logger.info("Disconnecting from database")
        await engine.dispose()
        logger.success("Database disconnected successfully")
    except Exception as e:
        logger.error(f"Error disconnecting from database: {e}")
        raise e
