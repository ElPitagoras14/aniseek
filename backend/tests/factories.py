"""Builds the minimal rows each test scenario needs (design D8). Data is
constructed per test, not seeded once, because the truncation between tests
(design D4) would erase any preseeded set anyway."""

import uuid


async def create_user(conn, *, username: str | None = None, role_name: str = "member") -> str:
    role_id = await conn.fetchval("SELECT id FROM role_types WHERE name = $1", role_name)
    if role_id is None:
        raise ValueError(f"Unknown seeded role: {role_name!r}")

    user_id = uuid.uuid4()
    username = username or f"user-{user_id.hex[:8]}"
    await conn.execute(
        """
        INSERT INTO users (id, username, password, role_id)
        VALUES ($1, $2, $3, $4)
        """,
        user_id,
        username,
        "not-a-real-hash",
        role_id,
    )
    return str(user_id)


async def create_anime(conn, *, anime_id: str | None = None, title: str = "Test Anime", **fields) -> str:
    anime_id = anime_id or f"anime-{uuid.uuid4().hex[:8]}"
    columns = {"id": anime_id, "title": title, **fields}
    col_names = ", ".join(columns)
    placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
    await conn.execute(
        f"INSERT INTO animes ({col_names}) VALUES ({placeholders})",
        *columns.values(),
    )
    return anime_id


async def create_episode(
    conn, *, anime_id: str, ep_number: int = 1, url: str | None = None, **fields
) -> int:
    url = url or f"https://example.test/{anime_id}/{ep_number}"
    columns = {"anime_id": anime_id, "ep_number": ep_number, "url": url, **fields}
    col_names = ", ".join(columns)
    placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
    return await conn.fetchval(
        f"INSERT INTO episodes ({col_names}) VALUES ({placeholders}) RETURNING id",
        *columns.values(),
    )
