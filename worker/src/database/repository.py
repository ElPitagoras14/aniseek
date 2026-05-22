from .client import db


async def get_episode_franchise_and_season(anime_id: str) -> tuple[str | None, int] | None:
    """Returns (franchise_id, season) of the anime, or None if not found."""
    query = """
        SELECT franchise_id, season
        FROM animes
        WHERE id = :anime_id
    """
    row = await db.fetch_one(query, {"anime_id": anime_id})
    if row is None:
        return None
    return row["franchise_id"], row["season"]


async def update_episode_status(
    anime_id: str,
    episode_number: int,
    status: str,
) -> None:
    """Update only episode status (no job_id change)."""
    query = """
        UPDATE episodes
        SET status = :status, updated_at = CURRENT_TIMESTAMP
        WHERE anime_id = :anime_id AND ep_number = :ep_number
    """
    await db.execute(query, {"status": status, "anime_id": anime_id, "ep_number": episode_number})


async def update_episode_status_and_job(
    anime_id: str,
    episode_number: int,
    status: str,
    job_id: str,
) -> None:
    """Update episode status and set job_id."""
    query = """
        UPDATE episodes
        SET status = :status, job_id = :job_id, updated_at = CURRENT_TIMESTAMP
        WHERE anime_id = :anime_id AND ep_number = :ep_number
    """
    await db.execute(
        query,
        {"status": status, "job_id": job_id, "anime_id": anime_id, "ep_number": episode_number},
    )


async def update_episode_status_clear_job(
    anime_id: str,
    episode_number: int,
    status: str,
) -> None:
    """Update episode status and set job_id to NULL."""
    query = """
        UPDATE episodes
        SET status = :status, job_id = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE anime_id = :anime_id AND ep_number = :ep_number
    """
    await db.execute(query, {"status": status, "anime_id": anime_id, "ep_number": episode_number})


async def update_episode_size(
    anime_id: str, episode_number: int, size: int
) -> None:
    query = """
        UPDATE episodes
        SET size = :size, updated_at = CURRENT_TIMESTAMP
        WHERE anime_id = :anime_id AND ep_number = :ep_number
    """
    await db.execute(
        query,
        {"size": size, "anime_id": anime_id, "ep_number": episode_number},
    )


async def get_started_download_count(franchise_id: str) -> int:
    query = """
        SELECT COUNT(DISTINCT e.id)
        FROM animes a
        INNER JOIN episodes e ON e.anime_id = a.id
        WHERE a.franchise_id = :franchise_id
          AND e.status NOT IN ('PENDING', 'SUCCESS', 'FAILED')
    """
    return await db.fetch_val(query, {"franchise_id": franchise_id}) or 0


async def list_franchise_animes(franchise_id: str) -> list[dict]:
    """Returns list of {id, season} dicts for every anime in the franchise."""
    query = """
        SELECT id, season
        FROM animes
        WHERE franchise_id = :franchise_id
    """
    rows = await db.fetch_all(query, {"franchise_id": franchise_id})
    return [dict(r) for r in rows]


async def update_anime_season(anime_id: str, season: int) -> None:
    query = """
        UPDATE animes
        SET season = :season
        WHERE id = :anime_id
    """
    await db.execute(query, {"season": season, "anime_id": anime_id})
