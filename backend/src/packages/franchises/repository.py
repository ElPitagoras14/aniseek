from sqlalchemy.ext.asyncio import AsyncConnection

from database.client import execute, fetch_all, fetch_one


async def list_franchises_with_animes(conn: AsyncConnection) -> list[dict]:
    query = """
        SELECT
            f.id AS franchise_id, f.name AS franchise_name,
            a.id AS anime_id, a.title, a.type, a.poster, a.created_at AS anime_created_at
        FROM franchises f
        LEFT JOIN animes a ON a.franchise_id = f.id
        ORDER BY f.name, a.title
    """
    rows = await fetch_all(conn, query)
    return [dict(row) for row in rows]


async def get_animes_by_ids(conn: AsyncConnection, anime_ids: list[str]) -> list[dict]:
    if not anime_ids:
        return []
    query = """
        SELECT id, title, season, type, poster, created_at, franchise_id
        FROM animes
        WHERE id = ANY(:ids)
    """
    rows = await fetch_all(conn, query, {"ids": anime_ids})
    return [dict(row) for row in rows]


async def insert_franchise(conn: AsyncConnection, franchise_id: str, name: str) -> None:
    query = """
        INSERT INTO franchises (id, name)
        VALUES (:id, :name)
    """
    await execute(conn, query, {"id": franchise_id, "name": name})


async def assign_animes_to_franchise(
    conn: AsyncConnection, anime_ids: list[str], franchise_id: str
) -> None:
    if not anime_ids:
        return
    query = """
        UPDATE animes
        SET franchise_id = :franchise_id
        WHERE id = ANY(:ids)
    """
    await execute(conn, query, {"franchise_id": franchise_id, "ids": anime_ids})


async def get_franchise_by_id(conn: AsyncConnection, franchise_id: str) -> dict | None:
    query = "SELECT id, name, created_at FROM franchises WHERE id = :id"
    row = await fetch_one(conn, query, {"id": franchise_id})
    return dict(row) if row else None


async def get_anime_without_franchise(conn: AsyncConnection, anime_id: str) -> dict | None:
    query = """
        SELECT id, title, type, poster, franchise_id
        FROM animes
        WHERE id = :id AND franchise_id IS NULL
    """
    row = await fetch_one(conn, query, {"id": anime_id})
    return dict(row) if row else None


async def list_animes_without_franchise(conn: AsyncConnection) -> list[dict]:
    query = """
        SELECT
            a.id, a.title, a.type, a.poster, a.created_at
        FROM animes a
        WHERE a.poster IS NOT NULL
          AND a.franchise_id IS NULL
        ORDER BY a.title ASC
    """
    rows = await fetch_all(conn, query)
    return [dict(row) for row in rows]
