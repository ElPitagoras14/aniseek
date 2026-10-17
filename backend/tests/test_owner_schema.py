"""Schema-level invariants of users-and-access: a single owner."""

import asyncpg
import pytest
from factories import create_user


async def test_database_rejects_a_second_owner(raw_conn):
    first = await create_user(raw_conn, role_name="owner")

    with pytest.raises(asyncpg.UniqueViolationError, match="uq_users_single_owner"):
        await create_user(raw_conn, role_name="owner")

    owners = await raw_conn.fetch(
        "SELECT u.id FROM users u JOIN role_types r ON r.id = u.role_id WHERE r.name = 'owner'"
    )
    assert [str(r["id"]) for r in owners] == [first]
