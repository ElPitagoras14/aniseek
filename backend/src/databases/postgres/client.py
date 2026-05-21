import time

from loguru import logger
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import postgres_settings

POSTGRES_URL = postgres_settings.POSTGRES_URL

if POSTGRES_URL.startswith("postgresql"):
    POSTGRES_URL = POSTGRES_URL.replace("postgresql", "postgresql+asyncpg")

host = POSTGRES_URL.split("@")[1].split(":")[0]
port = POSTGRES_URL.split(":")[2].split("/")[0]
user = POSTGRES_URL.split(":")[1].split("@")[0]
database = POSTGRES_URL.split("/")[1]

RETRIES = 5
DELAY = 5

for _ in range(RETRIES):
    try:
        engine = create_async_engine(
            POSTGRES_URL,
            pool_size=10,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=1800,
            echo=False,
        )
        break
    except OperationalError:
        logger.error(
            f"Could not connect to the database {database} on "
            + f"{host}:{port} as {user}. Retrying in {DELAY} seconds."
        )
        time.sleep(DELAY)
else:
    logger.error(
        f"Could not connect to the database {database} on "
        + f"{host}:{port} as {user}. Exiting."
    )
    exit(1)


AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
)


class AsyncDatabaseSession:
    def __init__(self):
        self.db: AsyncSession | None = None

    async def __aenter__(self) -> AsyncSession:
        self.db = AsyncSessionLocal()
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                await self.db.commit()
            else:
                await self.db.rollback()
                logger.error(f"DB rollback due to: {exc_val}")
        finally:
            await self.db.close()
