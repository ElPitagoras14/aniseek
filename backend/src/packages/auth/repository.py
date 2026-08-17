from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from database.client import fetch_one, fetch_val, execute


async def get_user_by_username(conn: AsyncConnection, username: str) -> dict | None:
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
    row = await fetch_one(conn, query, {"username": username})
    return dict(row) if row else None


async def get_user_by_id(conn: AsyncConnection, user_id: str) -> dict | None:
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
    row = await fetch_one(conn, query, {"user_id": UUID(user_id)})
    return dict(row) if row else None


async def get_user_id_by_username(conn: AsyncConnection, username: str) -> str | None:
    query = "SELECT id FROM users WHERE username = :username"
    return await fetch_val(conn, query, {"username": username})


async def insert_user(
    conn: AsyncConnection, username: str, hashed_password: str, role_id: int = 2
) -> None:
    query = """
        INSERT INTO users (id, username, password, role_id)
        VALUES (gen_random_uuid(), :username, :password, :role_id)
    """
    await execute(
        conn,
        query,
        {"username": username, "password": hashed_password, "role_id": role_id},
    )
