from uuid import UUID

from database.client import db


async def get_user_with_role_and_avatar_by_username(username: str) -> dict | None:
    query = """
        SELECT
            u.id, u.username, u.password, u.is_active,
            u.avatar_id, u.role_id,
            r.name AS role_name,
            a.url AS avatar_url,
            a.label AS avatar_label
        FROM users u
        LEFT JOIN role_types r ON r.id = u.role_id
        LEFT JOIN avatars a ON a.id = u.avatar_id
        WHERE u.username = :username
    """
    row = await db.fetch_one(query, {"username": username})
    return dict(row) if row else None


async def get_user_with_role_and_avatar_by_id(user_id: str) -> dict | None:
    query = """
        SELECT
            u.id, u.username, u.password, u.is_active,
            u.avatar_id, u.role_id,
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


async def get_user_id_by_username(username: str) -> str | None:
    query = "SELECT id FROM users WHERE username = :username"
    return await db.fetch_val(query, {"username": username})


async def insert_user(username: str, hashed_password: str, role_id: int = 2) -> None:
    query = """
        INSERT INTO users (id, username, password, role_id)
        VALUES (gen_random_uuid(), :username, :password, :role_id)
    """
    await db.execute(
        query,
        {"username": username, "password": hashed_password, "role_id": role_id},
    )
