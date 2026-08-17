"""Verifies the test harness itself before writing tests that depend on it
(migration plan step 5): a trivial insert/read, isolation between tests, that
no wrapping transaction hides commits from other connections, and that
truncation survives repeated runs without touching reference data.
"""

import os

import asyncpg
from dbutils import truncate_mutable_tables
from factories import create_anime


def test_can_import_an_app_module_the_way_the_app_does():
    """1.3: `src` is the import root, so this is `from config import ...`, not a
    nested package import."""
    from config import general_settings

    assert general_settings.SECRET_KEY == "test-secret-key"


async def test_insert_and_read_a_row(raw_conn):
    anime_id = await create_anime(raw_conn, anime_id="smoke-anime-1")

    row = await raw_conn.fetchrow("SELECT id FROM animes WHERE id = $1", anime_id)

    assert row is not None
    assert row["id"] == anime_id


async def test_previous_row_is_gone(raw_conn):
    """Runs right after test_insert_and_read_a_row and must not see its row —
    exercises the autouse truncation fixture."""
    row = await raw_conn.fetchrow("SELECT id FROM animes WHERE id = $1", "smoke-anime-1")

    assert row is None


async def test_committed_writes_are_visible_from_an_unrelated_connection():
    """Proves the harness does not wrap the test in a transaction (design D4):
    if it did, the write below — made and committed through `db`, the
    application's own pool — would be invisible to `other_conn`, a brand-new
    connection unrelated to both `db` and the seeding pool."""
    from database.client import db

    anime_id = "smoke-anime-visibility"
    async with db.transaction():
        await db.execute(
            "INSERT INTO animes (id, title) VALUES (:id, :title)",
            {"id": anime_id, "title": "Visibility Check"},
        )

    other_conn = await asyncpg.connect(dsn=os.environ["DB_URL"])
    try:
        row = await other_conn.fetchrow("SELECT id FROM animes WHERE id = $1", anime_id)
    finally:
        await other_conn.close()

    assert row is not None


async def test_reference_data_survives_repeated_truncation(raw_conn):
    for _ in range(3):
        await truncate_mutable_tables(raw_conn)

    role_names = {r["name"] for r in await raw_conn.fetch("SELECT name FROM role_types")}
    related_type_names = {
        r["name"] for r in await raw_conn.fetch("SELECT name FROM related_types")
    }
    avatar_count = await raw_conn.fetchval("SELECT count(*) FROM avatars")

    assert role_names == {"admin", "member", "guest"}
    assert related_type_names == {"prequel", "sequel", "alternative", "spin_off"}
    assert avatar_count > 0
