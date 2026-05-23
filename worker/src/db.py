from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import general_settings

engine: Engine = create_engine(
    general_settings.POSTGRES_URL,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800,
)


def execute(sql: str, params: dict | None = None) -> None:
    """Run a write query inside an auto-committed transaction."""
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})


def fetch_one(sql: str, params: dict | None = None):
    """Return the first matching row as a dict-like mapping, or None."""
    with engine.connect() as conn:
        return conn.execute(text(sql), params or {}).mappings().first()


def fetch_all(sql: str, params: dict | None = None):
    """Return all matching rows as dict-like mappings."""
    with engine.connect() as conn:
        return conn.execute(text(sql), params or {}).mappings().all()


def fetch_val(sql: str, params: dict | None = None):
    """Return the first column of the first row, or None."""
    with engine.connect() as conn:
        return conn.execute(text(sql), params or {}).scalar()


try:
    with engine.connect() as _conn:
        _conn.execute(text("SELECT 1"))
    logger.success("Database engine connected")
except Exception as e:
    logger.error(f"Database engine failed to connect: {e}")
    raise


# Sentinel: distinguishes "don't touch job_id" from "set job_id to NULL"
_UNSET = object()


def get_episode_franchise_and_season(anime_id: str) -> tuple[str | None, int] | None:
    row = fetch_one(
        "SELECT franchise_id, season FROM animes WHERE id = :anime_id",
        {"anime_id": anime_id},
    )
    if row is None:
        return None
    return row["franchise_id"], row["season"]


def update_episode_status(
    anime_id: str,
    episode_number: int,
    status: str,
    *,
    job_id: str | None | object = _UNSET,
) -> None:
    sets = ["status = :status", "updated_at = CURRENT_TIMESTAMP"]
    params: dict = {"status": status, "anime_id": anime_id, "ep_number": episode_number}
    if job_id is not _UNSET:
        sets.append("job_id = :job_id")
        params["job_id"] = job_id
    execute(
        f"UPDATE episodes SET {', '.join(sets)} WHERE anime_id = :anime_id AND ep_number = :ep_number",
        params,
    )


def update_episode_size(anime_id: str, episode_number: int, size: int) -> None:
    execute(
        "UPDATE episodes SET size = :size, updated_at = CURRENT_TIMESTAMP WHERE anime_id = :anime_id AND ep_number = :ep_number",
        {"size": size, "anime_id": anime_id, "ep_number": episode_number},
    )


def get_started_download_count(franchise_id: str) -> int:
    return (
        fetch_val(
            """
            SELECT COUNT(DISTINCT e.id)
            FROM animes a
            INNER JOIN episodes e ON e.anime_id = a.id
            WHERE a.franchise_id = :franchise_id
              AND e.status NOT IN ('PENDING', 'SUCCESS', 'FAILED')
            """,
            {"franchise_id": franchise_id},
        )
        or 0
    )


def list_franchise_animes(franchise_id: str):
    return fetch_all(
        "SELECT id, season FROM animes WHERE franchise_id = :franchise_id",
        {"franchise_id": franchise_id},
    )


def update_anime_season(anime_id: str, season: int) -> None:
    execute(
        "UPDATE animes SET season = :season WHERE id = :anime_id",
        {"season": season, "anime_id": anime_id},
    )
