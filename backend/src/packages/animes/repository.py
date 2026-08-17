from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from database.client import execute, execute_many, fetch_all, fetch_one, fetch_val


async def get_anime_by_id(conn: AsyncConnection, anime_id: str) -> dict | None:
    query = """
        SELECT id, title, description, type, poster, season,
               is_finished, week_day, franchise_id, last_scraped_at, created_at
        FROM animes
        WHERE id = :anime_id
    """
    row = await fetch_one(conn, query, {"anime_id": anime_id})
    return dict(row) if row else None


async def get_anime_with_relations(
    conn: AsyncConnection, anime_id: str, user_id: str | None = None
) -> dict | None:
    """Loads anime with genres, episodes (with per-user download flags), relations, and saved info."""
    anime = await get_anime_by_id(conn, anime_id)
    if not anime:
        return None

    genres = await fetch_all(
        conn,
        "SELECT name FROM genres WHERE anime_id = :id ORDER BY name",
        {"id": anime_id},
    )

    if user_id:
        episodes = await fetch_all(
            conn,
            """
            SELECT
                e.id, e.anime_id, e.ep_number, e.preview, e.url, e.job_id, e.status, e.size,
                (ude_user.user_id IS NOT NULL) AS is_user_downloaded,
                EXISTS (
                    SELECT 1 FROM user_download_episode ude WHERE ude.episode_id = e.id
                ) AS is_global_downloaded
            FROM episodes e
            LEFT JOIN user_download_episode ude_user
                   ON ude_user.episode_id = e.id AND ude_user.user_id = :user_id
            WHERE e.anime_id = :id
            ORDER BY e.ep_number
            """,
            {"id": anime_id, "user_id": UUID(user_id)},
        )
        saved_row = await fetch_one(
            conn,
            "SELECT created_at FROM user_save_anime WHERE user_id = :user_id AND anime_id = :anime_id",
            {"user_id": UUID(user_id), "anime_id": anime_id},
        )
        anime["saved_info"] = {
            "is_saved": saved_row is not None,
            "save_date": saved_row["created_at"] if saved_row else None,
        }
    else:
        episodes = await fetch_all(
            conn,
            """
            SELECT id, anime_id, ep_number, preview, url, job_id, status, size,
                   FALSE AS is_user_downloaded, FALSE AS is_global_downloaded
            FROM episodes WHERE anime_id = :id ORDER BY ep_number
            """,
            {"id": anime_id},
        )
        anime["saved_info"] = {"is_saved": False, "save_date": None}

    relations = await fetch_all(
        conn,
        """
        SELECT
            ar.related_anime_id,
            ra.title AS related_title,
            rt.name AS type_related_name
        FROM anime_relations ar
        INNER JOIN animes ra ON ra.id = ar.related_anime_id
        INNER JOIN related_types rt ON rt.id = ar.type_related_id
        WHERE ar.anime_id = :id
        """,
        {"id": anime_id},
    )

    anime["genres"] = [g["name"] for g in genres]
    anime["episodes"] = [dict(e) for e in episodes]
    anime["relations"] = [
        {
            "related_anime_id": r["related_anime_id"],
            "related_title": r["related_title"],
            "type_related_name": r["type_related_name"],
        }
        for r in relations
    ]
    return anime


async def upsert_scraped_anime(conn: AsyncConnection, values: dict) -> None:
    """INSERT with ON CONFLICT DO UPDATE — for scraped animes with full data."""
    query = """
        INSERT INTO animes (id, title, description, poster, type, is_finished, week_day, last_scraped_at)
        VALUES (:id, :title, :description, :poster, :type, :is_finished, :week_day, :last_scraped_at)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            poster = EXCLUDED.poster,
            type = EXCLUDED.type,
            is_finished = EXCLUDED.is_finished,
            week_day = EXCLUDED.week_day,
            last_scraped_at = EXCLUDED.last_scraped_at
    """
    await execute(conn, query, values)


async def insert_dummy_anime(conn: AsyncConnection, anime_id: str, title: str) -> None:
    """INSERT with ON CONFLICT DO NOTHING — for placeholder animes used in relations."""
    query = """
        INSERT INTO animes (id, title)
        VALUES (:id, :title)
        ON CONFLICT (id) DO NOTHING
    """
    await execute(conn, query, {"id": anime_id, "title": title})


async def insert_genres(conn: AsyncConnection, anime_id: str, names: list[str]) -> None:
    if not names:
        return
    query = """
        INSERT INTO genres (anime_id, name)
        VALUES (:anime_id, :name)
        ON CONFLICT (anime_id, name) DO NOTHING
    """
    await execute_many(conn, query, [{"anime_id": anime_id, "name": n} for n in names])


async def insert_anime_relation(
    conn: AsyncConnection, anime_id: str, related_anime_id: str, type_related_id: int
) -> None:
    query = """
        INSERT INTO anime_relations (anime_id, related_anime_id, type_related_id)
        VALUES (:anime_id, :related_anime_id, :type_related_id)
        ON CONFLICT (anime_id, related_anime_id, type_related_id) DO NOTHING
    """
    await execute(
        conn,
        query,
        {
            "anime_id": anime_id,
            "related_anime_id": related_anime_id,
            "type_related_id": type_related_id,
        },
    )


async def insert_episodes(conn: AsyncConnection, episodes: list[dict]) -> None:
    if not episodes:
        return
    query = """
        INSERT INTO episodes (anime_id, ep_number, preview, url)
        VALUES (:anime_id, :ep_number, :preview, :url)
        ON CONFLICT (anime_id, ep_number) DO NOTHING
    """
    await execute_many(conn, query, episodes)


async def update_anime_fields(conn: AsyncConnection, anime_id: str, values: dict) -> None:
    query = """
        UPDATE animes SET
            title = :title,
            description = :description,
            poster = :poster,
            type = :type,
            is_finished = :is_finished,
            week_day = :week_day,
            last_scraped_at = :last_scraped_at
        WHERE id = :anime_id
    """
    await execute(conn, query, {"anime_id": anime_id, **values})


async def get_max_episode_number(conn: AsyncConnection, anime_id: str) -> int:
    query = "SELECT COALESCE(MAX(ep_number), 0) FROM episodes WHERE anime_id = :id"
    return await fetch_val(conn, query, {"id": anime_id}) or 0


async def get_user_saved_anime(
    conn: AsyncConnection, user_id: str, anime_id: str
) -> dict | None:
    query = """
        SELECT user_id, anime_id, created_at
        FROM user_save_anime
        WHERE user_id = :user_id AND anime_id = :anime_id
    """
    row = await fetch_one(conn, query, {"user_id": UUID(user_id), "anime_id": anime_id})
    return dict(row) if row else None


async def list_user_saved_animes(conn: AsyncConnection, user_id: str) -> list[dict]:
    query = """
        SELECT
            a.id, a.title, a.type, a.poster, a.created_at, a.week_day, a.is_finished,
            usa.created_at AS save_date
        FROM user_save_anime usa
        INNER JOIN animes a ON a.id = usa.anime_id
        WHERE usa.user_id = :user_id
        ORDER BY usa.created_at DESC
    """
    rows = await fetch_all(conn, query, {"user_id": UUID(user_id)})
    return [dict(r) for r in rows]


async def list_user_saved_in_emission_animes(
    conn: AsyncConnection, user_id: str
) -> list[dict]:
    query = """
        SELECT
            a.id, a.title, a.type, a.poster, a.created_at, a.week_day,
            usa.created_at AS save_date
        FROM user_save_anime usa
        INNER JOIN animes a ON a.id = usa.anime_id
        WHERE usa.user_id = :user_id
          AND a.week_day IS NOT NULL
          AND a.is_finished IS FALSE
    """
    rows = await fetch_all(conn, query, {"user_id": UUID(user_id)})
    return [dict(r) for r in rows]


async def insert_user_saved_anime(conn: AsyncConnection, user_id: str, anime_id: str) -> None:
    query = """
        INSERT INTO user_save_anime (user_id, anime_id)
        VALUES (:user_id, :anime_id)
    """
    await execute(conn, query, {"user_id": UUID(user_id), "anime_id": anime_id})


async def delete_user_saved_anime(conn: AsyncConnection, user_id: str, anime_id: str) -> None:
    query = """
        DELETE FROM user_save_anime
        WHERE user_id = :user_id AND anime_id = :anime_id
    """
    await execute(conn, query, {"user_id": UUID(user_id), "anime_id": anime_id})


async def insert_new_episodes(
    conn: AsyncConnection, anime_id: str, episodes: list[dict]
) -> None:
    if not episodes:
        return
    query = """
        INSERT INTO episodes (anime_id, ep_number, preview, url)
        VALUES (:anime_id, :ep_number, :preview, :url)
        ON CONFLICT (anime_id, ep_number) DO NOTHING
    """
    await execute_many(conn, query, episodes)
