from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from database.client import fetch_one, fetch_val, execute

_USER_COLUMNS = """
    u.id, u.username, u.password, u.is_active,
    u.avatar_id, u.role_id, u.created_at, u.credentials_changed_at,
    r.name AS role_name,
    a.url AS avatar_url,
    a.label AS avatar_label
"""

_USER_JOINS = """
    FROM users u
    LEFT JOIN role_types r ON r.id = u.role_id
    LEFT JOIN avatars a ON a.id = u.avatar_id
"""


async def get_user_by_username(conn: AsyncConnection, username: str) -> dict | None:
    query = f"SELECT {_USER_COLUMNS} {_USER_JOINS} WHERE u.username = :username"
    row = await fetch_one(conn, query, {"username": username})
    return dict(row) if row else None


async def get_user_by_id(conn: AsyncConnection, user_id: str) -> dict | None:
    query = f"SELECT {_USER_COLUMNS} {_USER_JOINS} WHERE u.id = :user_id"
    row = await fetch_one(conn, query, {"user_id": UUID(user_id)})
    return dict(row) if row else None


async def get_owner_user(conn: AsyncConnection) -> dict | None:
    query = f"SELECT {_USER_COLUMNS} {_USER_JOINS} WHERE r.name = 'owner'"
    row = await fetch_one(conn, query)
    return dict(row) if row else None


async def get_user_by_api_key_hash(conn: AsyncConnection, key_hash: str) -> dict | None:
    query = f"""
        SELECT {_USER_COLUMNS} {_USER_JOINS}
        JOIN api_keys k ON k.user_id = u.id
        WHERE k.key_hash = :key_hash
    """
    row = await fetch_one(conn, query, {"key_hash": key_hash})
    return dict(row) if row else None


async def touch_api_key(conn: AsyncConnection, user_id: str | UUID) -> None:
    """Records the key's last use, at most once a minute (design D5): an MCP
    session sends bursts of calls and each one shouldn't be a write."""
    query = """
        UPDATE api_keys SET last_used_at = CURRENT_TIMESTAMP
        WHERE user_id = :user_id
          AND (last_used_at IS NULL
               OR last_used_at < CURRENT_TIMESTAMP - INTERVAL '1 minute')
    """
    await execute(conn, query, {"user_id": UUID(str(user_id))})


async def get_user_id_by_username(conn: AsyncConnection, username: str) -> str | None:
    query = "SELECT id FROM users WHERE username = :username"
    return await fetch_val(conn, query, {"username": username})


async def insert_user(
    conn: AsyncConnection,
    username: str,
    hashed_password: str,
    role_name: str = "member",
) -> UUID:
    """Inserts a user with the role resolved by name (never by id) and returns
    its id. Fails if the role does not exist."""
    query = """
        INSERT INTO users (id, username, password, role_id)
        VALUES (
            gen_random_uuid(), :username, :password,
            (SELECT id FROM role_types WHERE name = :role_name)
        )
        RETURNING id
    """
    return await fetch_val(
        conn,
        query,
        {"username": username, "password": hashed_password, "role_name": role_name},
    )


async def get_owner_id(conn: AsyncConnection) -> UUID | None:
    query = """
        SELECT u.id FROM users u
        JOIN role_types r ON r.id = u.role_id
        WHERE r.name = 'owner'
    """
    return await fetch_val(conn, query)


async def get_oldest_active_admin_id(conn: AsyncConnection) -> UUID | None:
    query = """
        SELECT u.id FROM users u
        JOIN role_types r ON r.id = u.role_id
        WHERE r.name = 'admin' AND u.is_active
        ORDER BY u.created_at, u.id
        LIMIT 1
    """
    return await fetch_val(conn, query)


async def set_user_role(conn: AsyncConnection, user_id: str | UUID, role_name: str) -> None:
    query = """
        UPDATE users
        SET role_id = (SELECT id FROM role_types WHERE name = :role_name),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :user_id
    """
    await execute(
        conn, query, {"user_id": UUID(str(user_id)), "role_name": role_name}
    )


async def get_registration_policy(conn: AsyncConnection) -> str:
    return await fetch_val(conn, "SELECT registration_policy FROM instance_settings")


async def consume_invitation(conn: AsyncConnection, token_hash: str) -> dict | None:
    """Atomically marks a pending invitation as used (design D8). The UPDATE
    locks the row, so of two concurrent registrations only one gets it back."""
    query = """
        UPDATE invitations i
        SET used_at = CURRENT_TIMESTAMP
        FROM role_types r
        WHERE r.id = i.role_id
          AND i.token_hash = :token_hash
          AND i.used_at IS NULL
          AND i.revoked_at IS NULL
          AND i.expires_at > CURRENT_TIMESTAMP
        RETURNING i.id, r.name AS role_name
    """
    row = await fetch_one(conn, query, {"token_hash": token_hash})
    return dict(row) if row else None


async def set_invitation_used_by(
    conn: AsyncConnection, invitation_id: UUID, user_id: UUID
) -> None:
    query = "UPDATE invitations SET used_by = :user_id WHERE id = :invitation_id"
    await execute(conn, query, {"user_id": user_id, "invitation_id": invitation_id})
