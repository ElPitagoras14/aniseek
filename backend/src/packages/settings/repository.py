from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from database.client import execute, fetch_one


async def get_settings(conn: AsyncConnection) -> dict:
    row = await fetch_one(
        conn, "SELECT registration_policy, updated_at FROM instance_settings"
    )
    return dict(row)


async def update_registration_policy(
    conn: AsyncConnection, policy: str, updated_by: str
) -> None:
    query = """
        UPDATE instance_settings
        SET registration_policy = :policy,
            updated_by = :updated_by,
            updated_at = CURRENT_TIMESTAMP
    """
    await execute(conn, query, {"policy": policy, "updated_by": UUID(updated_by)})
