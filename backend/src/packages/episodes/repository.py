from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from database.client import execute, fetch_all, fetch_one, fetch_val


async def get_episode_with_anime(
    conn: AsyncConnection, episode_id: int, anime_id: str | None = None
) -> dict | None:
    query = """
        SELECT
            e.id, e.anime_id, e.ep_number, e.preview, e.url, e.job_id, e.status, e.size,
            a.title AS anime_title, a.poster AS anime_poster,
            a.season AS anime_season, a.franchise_id AS anime_franchise_id
        FROM episodes e
        INNER JOIN animes a ON a.id = e.anime_id
        WHERE e.id = :episode_id
    """
    values: dict = {"episode_id": episode_id}
    if anime_id:
        query += " AND e.anime_id = :anime_id"
        values["anime_id"] = anime_id

    row = await fetch_one(conn, query, values)
    return dict(row) if row else None


async def get_episodes_with_user_download_status(
    conn: AsyncConnection, anime_id: str, ep_numbers: list[int], user_id: str
) -> list[dict]:
    """Batch lookup: returns episodes for the given numbers with a flag indicating
    whether the user already has a download record for each."""
    if not ep_numbers:
        return []
    query = """
        SELECT
            e.id, e.anime_id, e.ep_number, e.preview, e.url, e.job_id, e.status, e.size,
            a.title AS anime_title, a.poster AS anime_poster,
            a.season AS anime_season, a.franchise_id AS anime_franchise_id,
            (ude.user_id IS NOT NULL) AS already_downloaded
        FROM episodes e
        INNER JOIN animes a ON a.id = e.anime_id
        LEFT JOIN user_download_episode ude
               ON ude.episode_id = e.id AND ude.user_id = :user_id
        WHERE e.anime_id = :anime_id AND e.ep_number = ANY(:ep_numbers)
    """
    rows = await fetch_all(
        conn,
        query,
        {"anime_id": anime_id, "ep_numbers": ep_numbers, "user_id": UUID(user_id)},
    )
    return [dict(r) for r in rows]


async def get_episode_by_anime_and_number(
    conn: AsyncConnection, anime_id: str, ep_number: int
) -> dict | None:
    query = """
        SELECT
            e.id, e.anime_id, e.ep_number, e.preview, e.url, e.job_id, e.status, e.size,
            a.title AS anime_title, a.poster AS anime_poster,
            a.season AS anime_season, a.franchise_id AS anime_franchise_id
        FROM episodes e
        INNER JOIN animes a ON a.id = e.anime_id
        WHERE e.anime_id = :anime_id AND e.ep_number = :ep_number
    """
    row = await fetch_one(conn, query, {"anime_id": anime_id, "ep_number": ep_number})
    return dict(row) if row else None


async def get_user_episode_download(
    conn: AsyncConnection, user_id: str, episode_id: int
) -> dict | None:
    query = """
        SELECT user_id, episode_id, created_at
        FROM user_download_episode
        WHERE user_id = :user_id AND episode_id = :episode_id
    """
    row = await fetch_one(
        conn, query, {"user_id": UUID(user_id), "episode_id": episode_id}
    )
    return dict(row) if row else None


async def get_any_episode_download_with_job(
    conn: AsyncConnection, episode_id: int
) -> dict | None:
    """Returns any existing download record for the episode along with its current job_id."""
    query = """
        SELECT ude.user_id, ude.episode_id, e.job_id
        FROM user_download_episode ude
        INNER JOIN episodes e ON e.id = ude.episode_id
        WHERE ude.episode_id = :episode_id
        LIMIT 1
    """
    row = await fetch_one(conn, query, {"episode_id": episode_id})
    return dict(row) if row else None


async def insert_user_episode_download(
    conn: AsyncConnection, user_id: str, episode_id: int
) -> None:
    query = """
        INSERT INTO user_download_episode (user_id, episode_id)
        VALUES (:user_id, :episode_id)
        ON CONFLICT (user_id, episode_id) DO NOTHING
    """
    await execute(conn, query, {"user_id": UUID(user_id), "episode_id": episode_id})


async def update_episode_job(
    conn: AsyncConnection, episode_id: int, job_id: str, status: str
) -> None:
    query = """
        UPDATE episodes
        SET job_id = :job_id, status = :status, updated_at = CURRENT_TIMESTAMP
        WHERE id = :episode_id
    """
    await execute(
        conn, query, {"episode_id": episode_id, "job_id": job_id, "status": status}
    )


async def delete_user_episode_download(
    conn: AsyncConnection, user_id: str, episode_id: int
) -> None:
    query = """
        DELETE FROM user_download_episode
        WHERE user_id = :user_id AND episode_id = :episode_id
    """
    await execute(conn, query, {"user_id": UUID(user_id), "episode_id": episode_id})


async def count_episode_downloads(conn: AsyncConnection, episode_id: int) -> int:
    query = "SELECT COUNT(*) FROM user_download_episode WHERE episode_id = :id"
    return await fetch_val(conn, query, {"id": episode_id}) or 0


async def list_user_downloads(
    conn: AsyncConnection,
    user_id: str,
    anime_id: str | None = None,
    limit: int = 10,
    page: int = 1,
    q: str | None = None,
) -> tuple[int, list[dict]]:
    base = """
        FROM user_download_episode ude
        INNER JOIN episodes e ON e.id = ude.episode_id
        INNER JOIN animes a ON a.id = e.anime_id
        WHERE ude.user_id = :user_id
    """
    values: dict = {"user_id": UUID(user_id)}
    if anime_id:
        base += " AND a.id = :anime_id"
        values["anime_id"] = anime_id
    if q:
        base += " AND a.title ILIKE :q"
        values["q"] = f"%{q}%"

    count = await fetch_val(conn, f"SELECT COUNT(*) {base}", values) or 0

    list_query = (
        "SELECT ude.episode_id, ude.created_at AS downloaded_at, "
        "e.ep_number AS episode_number, e.job_id, e.size, e.status, "
        "a.id AS anime_id, a.title, a.poster "
        + base
        + " ORDER BY ude.created_at DESC OFFSET :offset LIMIT :limit"
    )
    values_list = {**values, "offset": (page - 1) * limit, "limit": limit}
    rows = await fetch_all(conn, list_query, values_list)
    return count, [dict(r) for r in rows]


async def list_last_user_downloads(
    conn: AsyncConnection, user_id: str, limit: int = 5
) -> list[dict]:
    query = """
        SELECT ude.episode_id, ude.created_at AS downloaded_at,
               e.ep_number AS episode_number, e.job_id, e.size, e.status,
               a.id AS anime_id, a.title, a.poster
        FROM user_download_episode ude
        INNER JOIN episodes e ON e.id = ude.episode_id
        INNER JOIN animes a ON a.id = e.anime_id
        WHERE ude.user_id = :user_id
        ORDER BY ude.created_at DESC
        LIMIT :limit
    """
    rows = await fetch_all(conn, query, {"user_id": UUID(user_id), "limit": limit})
    return [dict(r) for r in rows]


async def list_user_downloaded_animes(conn: AsyncConnection, user_id: str) -> list[dict]:
    query = """
        SELECT DISTINCT a.id, a.title
        FROM user_download_episode ude
        INNER JOIN episodes e ON e.id = ude.episode_id
        INNER JOIN animes a ON a.id = e.anime_id
        WHERE ude.user_id = :user_id
        ORDER BY a.title
    """
    rows = await fetch_all(conn, query, {"user_id": UUID(user_id)})
    return [dict(r) for r in rows]


async def list_animes_storage(
    conn: AsyncConnection, limit: int, offset: int, q: str | None = None
) -> tuple[int, int, list[dict]]:
    if q is not None:
        q_param = f"%{q}%"
        count_query = """
            SELECT COUNT(*) FROM (
                SELECT a.id
                FROM animes a
                INNER JOIN episodes e ON e.anime_id = a.id
                WHERE e.size IS NOT NULL AND a.title ILIKE :q
                GROUP BY a.id
            ) sub
        """
        count = await fetch_val(conn, count_query, {"q": q_param}) or 0

        total_size_query = """
            SELECT COALESCE(SUM(e.size), 0) AS total_size
            FROM animes a
            INNER JOIN episodes e ON e.anime_id = a.id
            WHERE e.size IS NOT NULL AND a.title ILIKE :q
        """
        total_size = await fetch_val(conn, total_size_query, {"q": q_param}) or 0

        list_query = """
            SELECT a.id, a.title, SUM(e.size) AS size
            FROM animes a
            INNER JOIN episodes e ON e.anime_id = a.id
            WHERE e.size IS NOT NULL AND a.title ILIKE :q
            GROUP BY a.id, a.title
            ORDER BY SUM(e.size) DESC
            OFFSET :offset LIMIT :limit
        """
        rows = await fetch_all(
            conn, list_query, {"q": q_param, "offset": offset, "limit": limit}
        )
    else:
        count_query = """
            SELECT COUNT(*) FROM (
                SELECT a.id
                FROM animes a
                INNER JOIN episodes e ON e.anime_id = a.id
                WHERE e.size IS NOT NULL
                GROUP BY a.id
            ) sub
        """
        count = await fetch_val(conn, count_query) or 0

        total_size_query = """
            SELECT COALESCE(SUM(e.size), 0) AS total_size
            FROM episodes e WHERE e.size IS NOT NULL
        """
        total_size = await fetch_val(conn, total_size_query) or 0

        list_query = """
            SELECT a.id, a.title, SUM(e.size) AS size
            FROM animes a
            INNER JOIN episodes e ON e.anime_id = a.id
            WHERE e.size IS NOT NULL
            GROUP BY a.id, a.title
            ORDER BY SUM(e.size) DESC
            OFFSET :offset LIMIT :limit
        """
        rows = await fetch_all(conn, list_query, {"offset": offset, "limit": limit})

    return count, total_size, [dict(r) for r in rows]


async def get_anime_with_episodes_for_storage(
    conn: AsyncConnection, anime_id: str
) -> dict | None:
    anime_row = await fetch_one(
        conn,
        "SELECT id, title, season, franchise_id FROM animes WHERE id = :id",
        {"id": anime_id},
    )
    if not anime_row:
        return None
    eps = await fetch_all(
        conn,
        "SELECT id, ep_number FROM episodes WHERE anime_id = :id",
        {"id": anime_id},
    )
    result = dict(anime_row)
    result["episodes"] = [dict(e) for e in eps]
    return result


async def delete_user_downloads_for_episodes(
    conn: AsyncConnection, episode_ids: list[int]
) -> None:
    if not episode_ids:
        return
    query = "DELETE FROM user_download_episode WHERE episode_id = ANY(:ids)"
    await execute(conn, query, {"ids": episode_ids})


async def reset_episodes_storage(conn: AsyncConnection, anime_id: str) -> None:
    query = """
        UPDATE episodes
        SET size = NULL, job_id = NULL, status = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE anime_id = :anime_id
    """
    await execute(conn, query, {"anime_id": anime_id})
