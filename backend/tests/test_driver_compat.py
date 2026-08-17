"""Exercises the two SQL patterns where psycopg3 and asyncpg could behave
differently (unify-database-access, Risks/Trade-offs): `execute_many` paired
with `ON CONFLICT ... DO NOTHING`, and a `COUNT(*)` read back through
`fetch_val`.
"""

import uuid

from factories import create_anime, create_episode, create_user


async def test_execute_many_with_on_conflict_do_nothing_skips_duplicates(raw_conn):
    from database.client import engine
    from packages.animes import repository

    anime_id = await create_anime(raw_conn)

    async with engine.begin() as conn:
        await repository.insert_genres(conn, anime_id, ["Action", "Comedy"])
        # Re-inserts "Action": execute_many must skip it via ON CONFLICT DO
        # NOTHING instead of erroring the whole batch.
        await repository.insert_genres(conn, anime_id, ["Action", "Drama"])

    rows = await raw_conn.fetch(
        "SELECT name FROM genres WHERE anime_id = $1 ORDER BY name", anime_id
    )
    assert {r["name"] for r in rows} == {"Action", "Comedy", "Drama"}


async def test_count_query_returns_a_python_int(raw_conn):
    from database.client import engine
    from packages.episodes import repository

    user_id = await create_user(raw_conn)
    anime_id = await create_anime(raw_conn)
    episode_id = await create_episode(raw_conn, anime_id=anime_id, ep_number=1)
    await raw_conn.execute(
        "INSERT INTO user_download_episode (user_id, episode_id) VALUES ($1, $2)",
        uuid.UUID(user_id),
        episode_id,
    )

    async with engine.connect() as conn:
        count = await repository.count_episode_downloads(conn, episode_id)

    assert count == 1
    assert isinstance(count, int)
