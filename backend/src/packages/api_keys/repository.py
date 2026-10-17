from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from database.client import fetch_all, fetch_one, fetch_val


async def get_api_key(conn: AsyncConnection, user_id: str) -> dict | None:
    """Never selects key_hash."""
    query = """
        SELECT prefix, created_at, last_used_at
        FROM api_keys WHERE user_id = :user_id
    """
    row = await fetch_one(conn, query, {"user_id": UUID(user_id)})
    return dict(row) if row else None


async def upsert_api_key(
    conn: AsyncConnection, user_id: str, prefix: str, key_hash: str
) -> dict:
    """Creates the user's key or replaces it (design D1). A single statement,
    so there is no moment where both keys, or neither, work."""
    query = """
        INSERT INTO api_keys (user_id, prefix, key_hash)
        VALUES (:user_id, :prefix, :key_hash)
        ON CONFLICT (user_id) DO UPDATE
        SET prefix = EXCLUDED.prefix,
            key_hash = EXCLUDED.key_hash,
            created_at = CURRENT_TIMESTAMP,
            last_used_at = NULL
        RETURNING prefix, created_at
    """
    row = await fetch_one(
        conn,
        query,
        {"user_id": UUID(user_id), "prefix": prefix, "key_hash": key_hash},
    )
    return dict(row)


async def delete_api_key(conn: AsyncConnection, user_id: str) -> bool:
    query = "DELETE FROM api_keys WHERE user_id = :user_id RETURNING user_id"
    return await fetch_val(conn, query, {"user_id": UUID(user_id)}) is not None


async def list_api_keys(conn: AsyncConnection) -> list[dict]:
    """Never selects key_hash."""
    query = """
        SELECT k.user_id, u.username, k.prefix, k.created_at, k.last_used_at
        FROM api_keys k
        JOIN users u ON u.id = k.user_id
        ORDER BY u.username
    """
    rows = await fetch_all(conn, query)
    return [dict(row) for row in rows]
