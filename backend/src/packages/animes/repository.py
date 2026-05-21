from uuid import UUID

from database.client import db


async def get_anime_by_id(anime_id: str) -> dict | None:
    query = """
        SELECT id, title, description, type, poster, season,
               is_finished, week_day, franchise_id, last_scraped_at, created_at
        FROM animes
        WHERE id = :anime_id
    """
    row = await db.fetch_one(query, {"anime_id": anime_id})
    return dict(row) if row else None


async def get_anime_with_relations(anime_id: str) -> dict | None:
    """Carga anime + genres + episodes + related animes."""
    anime = await get_anime_by_id(anime_id)
    if not anime:
        return None

    genres = await db.fetch_all(
        "SELECT name FROM genres WHERE anime_id = :id ORDER BY name",
        {"id": anime_id},
    )
    episodes = await db.fetch_all(
        """
        SELECT id, anime_id, ep_number, preview, url, job_id, status, size
        FROM episodes
        WHERE anime_id = :id
        ORDER BY ep_number
        """,
        {"id": anime_id},
    )
    relations = await db.fetch_all(
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


async def upsert_scraped_anime(values: dict) -> None:
    """INSERT con ON CONFLICT DO UPDATE — para animes scrapeados (datos reales)."""
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
    await db.execute(query, values)


async def insert_dummy_anime(anime_id: str, title: str) -> None:
    """INSERT con ON CONFLICT DO NOTHING — para animes relacionados (dummies)."""
    query = """
        INSERT INTO animes (id, title)
        VALUES (:id, :title)
        ON CONFLICT (id) DO NOTHING
    """
    await db.execute(query, {"id": anime_id, "title": title})


async def insert_genres(anime_id: str, names: list[str]) -> None:
    if not names:
        return
    query = """
        INSERT INTO genres (anime_id, name)
        VALUES (:anime_id, :name)
        ON CONFLICT (anime_id, name) DO NOTHING
    """
    await db.execute_many(
        query, [{"anime_id": anime_id, "name": n} for n in names]
    )


async def insert_anime_relation(
    anime_id: str, related_anime_id: str, type_related_id: int
) -> None:
    query = """
        INSERT INTO anime_relations (anime_id, related_anime_id, type_related_id)
        VALUES (:anime_id, :related_anime_id, :type_related_id)
        ON CONFLICT (anime_id, related_anime_id, type_related_id) DO NOTHING
    """
    await db.execute(
        query,
        {
            "anime_id": anime_id,
            "related_anime_id": related_anime_id,
            "type_related_id": type_related_id,
        },
    )


async def insert_episodes(episodes: list[dict]) -> None:
    if not episodes:
        return
    query = """
        INSERT INTO episodes (anime_id, ep_number, preview, url)
        VALUES (:anime_id, :ep_number, :preview, :url)
        ON CONFLICT (anime_id, ep_number) DO NOTHING
    """
    await db.execute_many(query, episodes)


async def update_anime_fields(anime_id: str, values: dict) -> None:
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
    await db.execute(query, {"anime_id": anime_id, **values})


async def get_max_episode_number(anime_id: str) -> int:
    query = "SELECT COALESCE(MAX(ep_number), 0) FROM episodes WHERE anime_id = :id"
    return await db.fetch_val(query, {"id": anime_id}) or 0


async def get_user_saved_anime(user_id: str, anime_id: str) -> dict | None:
    query = """
        SELECT user_id, anime_id, created_at
        FROM user_save_anime
        WHERE user_id = :user_id AND anime_id = :anime_id
    """
    row = await db.fetch_one(
        query, {"user_id": UUID(user_id), "anime_id": anime_id}
    )
    return dict(row) if row else None


async def get_episode_ids_by_anime(anime_id: str) -> list[int]:
    query = "SELECT id FROM episodes WHERE anime_id = :id"
    rows = await db.fetch_all(query, {"id": anime_id})
    return [r["id"] for r in rows]


async def get_user_downloaded_episode_ids(
    user_id: str, episode_ids: list[int]
) -> list[int]:
    if not episode_ids:
        return []
    query = """
        SELECT episode_id FROM user_download_episode
        WHERE user_id = :user_id AND episode_id = ANY(:ids)
    """
    rows = await db.fetch_all(
        query, {"user_id": UUID(user_id), "ids": episode_ids}
    )
    return [r["episode_id"] for r in rows]


async def get_global_downloaded_episode_ids(episode_ids: list[int]) -> list[int]:
    if not episode_ids:
        return []
    query = "SELECT DISTINCT episode_id FROM user_download_episode WHERE episode_id = ANY(:ids)"
    rows = await db.fetch_all(query, {"ids": episode_ids})
    return [r["episode_id"] for r in rows]


async def list_user_saved_animes(user_id: str) -> list[dict]:
    query = """
        SELECT
            a.id, a.title, a.type, a.poster, a.created_at, a.week_day, a.is_finished,
            usa.created_at AS save_date
        FROM user_save_anime usa
        INNER JOIN animes a ON a.id = usa.anime_id
        WHERE usa.user_id = :user_id
        ORDER BY usa.created_at DESC
    """
    rows = await db.fetch_all(query, {"user_id": UUID(user_id)})
    return [dict(r) for r in rows]


async def list_user_saved_in_emission_animes(user_id: str) -> list[dict]:
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
    rows = await db.fetch_all(query, {"user_id": UUID(user_id)})
    return [dict(r) for r in rows]


async def insert_user_saved_anime(user_id: str, anime_id: str) -> None:
    query = """
        INSERT INTO user_save_anime (user_id, anime_id)
        VALUES (:user_id, :anime_id)
    """
    await db.execute(query, {"user_id": UUID(user_id), "anime_id": anime_id})


async def delete_user_saved_anime(user_id: str, anime_id: str) -> None:
    query = """
        DELETE FROM user_save_anime
        WHERE user_id = :user_id AND anime_id = :anime_id
    """
    await db.execute(query, {"user_id": UUID(user_id), "anime_id": anime_id})


async def insert_new_episodes(anime_id: str, episodes: list[dict]) -> None:
    if not episodes:
        return
    query = """
        INSERT INTO episodes (anime_id, ep_number, preview, url)
        VALUES (:anime_id, :ep_number, :preview, :url)
        ON CONFLICT (anime_id, ep_number) DO NOTHING
    """
    await db.execute_many(query, episodes)
