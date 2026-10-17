from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from database.client import execute, fetch_all, fetch_one


async def insert_invitation(
    conn: AsyncConnection,
    invitation_id: UUID,
    token_hash: str,
    role_name: str,
    created_by: str,
    expires_at: datetime,
) -> None:
    query = """
        INSERT INTO invitations (id, token_hash, role_id, created_by, expires_at)
        VALUES (
            :id, :token_hash,
            (SELECT id FROM role_types WHERE name = :role_name),
            :created_by, :expires_at
        )
    """
    await execute(
        conn,
        query,
        {
            "id": invitation_id,
            "token_hash": token_hash,
            "role_name": role_name,
            "created_by": UUID(created_by),
            "expires_at": expires_at,
        },
    )


async def list_invitations(
    conn: AsyncConnection, role_name: str | None = None
) -> list[dict]:
    """Pending invitations (not used, not revoked, not expired) plus the ones
    already used, which carry who used them and when. Revoked and expired
    unused ones are hidden. Never selects token_hash."""
    query = """
        SELECT i.id, r.name AS role_name, i.created_at, i.expires_at, i.used_at,
               u.username AS created_by_username,
               uu.username AS used_by_username
        FROM invitations i
        JOIN role_types r ON r.id = i.role_id
        LEFT JOIN users u ON u.id = i.created_by
        LEFT JOIN users uu ON uu.id = i.used_by
        WHERE i.revoked_at IS NULL
          AND (i.used_at IS NOT NULL OR i.expires_at > CURRENT_TIMESTAMP)
          AND (CAST(:role_name AS TEXT) IS NULL OR r.name = :role_name)
        ORDER BY i.created_at DESC
    """
    rows = await fetch_all(conn, query, {"role_name": role_name})
    return [dict(row) for row in rows]


async def get_pending_invitation(
    conn: AsyncConnection, invitation_id: UUID
) -> dict | None:
    query = """
        SELECT i.id, r.name AS role_name
        FROM invitations i
        JOIN role_types r ON r.id = i.role_id
        WHERE i.id = :id
          AND i.used_at IS NULL
          AND i.revoked_at IS NULL
          AND i.expires_at > CURRENT_TIMESTAMP
    """
    row = await fetch_one(conn, query, {"id": invitation_id})
    return dict(row) if row else None


async def revoke_invitation(conn: AsyncConnection, invitation_id: UUID) -> None:
    query = """
        UPDATE invitations SET revoked_at = CURRENT_TIMESTAMP
        WHERE id = :id AND used_at IS NULL AND revoked_at IS NULL
    """
    await execute(conn, query, {"id": invitation_id})
