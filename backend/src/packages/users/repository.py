from uuid import UUID

from database.client import db


async def list_users_with_role_and_avatar() -> list[dict]:
    query = """
        SELECT
            u.id, u.username, u.is_active, u.created_at, u.updated_at,
            u.avatar_id, u.role_id,
            r.name AS role_name,
            a.url AS avatar_url,
            a.label AS avatar_label
        FROM users u
        LEFT JOIN role_types r ON r.id = u.role_id
        LEFT JOIN avatars a ON a.id = u.avatar_id
        ORDER BY u.created_at DESC
    """
    rows = await db.fetch_all(query)
    return [dict(row) for row in rows]


async def get_user_with_role(user_id: str) -> dict | None:
    query = """
        SELECT
            u.id, u.username, u.password, u.is_active,
            u.avatar_id, u.created_at, u.updated_at,
            r.name AS role_name
        FROM users u
        LEFT JOIN role_types r ON r.id = u.role_id
        WHERE u.id = :user_id
    """
    row = await db.fetch_one(query, {"user_id": UUID(user_id)})
    return dict(row) if row else None


async def get_avatar_by_id(avatar_id: int) -> dict | None:
    query = "SELECT id, label, url FROM avatars WHERE id = :avatar_id"
    row = await db.fetch_one(query, {"avatar_id": avatar_id})
    return dict(row) if row else None


async def username_exists(username: str) -> bool:
    query = "SELECT 1 FROM users WHERE username = :username"
    return await db.fetch_val(query, {"username": username}) is not None


async def list_avatars() -> list[dict]:
    query = "SELECT id, label, url FROM avatars ORDER BY id"
    rows = await db.fetch_all(query)
    return [dict(row) for row in rows]


async def update_user_username(user_id: str, username: str) -> None:
    query = """
        UPDATE users
        SET username = :username, updated_at = CURRENT_TIMESTAMP
        WHERE id = :user_id
    """
    await db.execute(query, {"user_id": UUID(user_id), "username": username})


async def update_user_password(user_id: str, hashed_password: str) -> None:
    query = """
        UPDATE users
        SET password = :password, updated_at = CURRENT_TIMESTAMP
        WHERE id = :user_id
    """
    await db.execute(query, {"user_id": UUID(user_id), "password": hashed_password})


async def get_user_current_password(user_id: str) -> str | None:
    query = "SELECT password FROM users WHERE id = :user_id"
    return await db.fetch_val(query, {"user_id": UUID(user_id)})


async def update_user_avatar(user_id: str, avatar_id: int) -> None:
    query = """
        UPDATE users
        SET avatar_id = :avatar_id, updated_at = CURRENT_TIMESTAMP
        WHERE id = :user_id
    """
    await db.execute(query, {"user_id": UUID(user_id), "avatar_id": avatar_id})


async def count_saved_animes(user_id: str) -> int:
    query = "SELECT COUNT(*) FROM user_save_anime WHERE user_id = :user_id"
    return await db.fetch_val(query, {"user_id": UUID(user_id)}) or 0


async def count_downloaded_episodes(user_id: str) -> int:
    query = "SELECT COUNT(*) FROM user_download_episode WHERE user_id = :user_id"
    return await db.fetch_val(query, {"user_id": UUID(user_id)}) or 0


async def get_user_by_id_with_role_and_avatar(user_id: str) -> dict | None:
    query = """
        SELECT
            u.id, u.username, u.is_active, u.created_at, u.updated_at,
            r.name AS role_name,
            a.url AS avatar_url,
            a.label AS avatar_label
        FROM users u
        LEFT JOIN role_types r ON r.id = u.role_id
        LEFT JOIN avatars a ON a.id = u.avatar_id
        WHERE u.id = :user_id
    """
    row = await db.fetch_one(query, {"user_id": UUID(user_id)})
    return dict(row) if row else None


async def get_user_by_username(username: str) -> dict | None:
    query = """
        SELECT id, username, is_active, created_at, updated_at
        FROM users
        WHERE username = :username
    """
    row = await db.fetch_one(query, {"username": username})
    return dict(row) if row else None


async def count_in_emission_saved_animes(user_id: str) -> int:
    query = """
        SELECT COUNT(*)
        FROM user_save_anime usa
        INNER JOIN animes a ON a.id = usa.anime_id
        WHERE usa.user_id = :user_id
          AND a.is_finished IS FALSE
    """
    return await db.fetch_val(query, {"user_id": UUID(user_id)}) or 0
