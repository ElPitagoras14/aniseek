from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from packages.auth import auth_scheme
from utils.exceptions import NotFoundException
from databases.postgres import AsyncDatabaseSession, Franchise, Anime


async def valid_franchise_id(
    franchise_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Valida que la franquicia existe y retorna los datos."""
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Franchise)
            .where(Franchise.id == franchise_id)
            .options(selectinload(Franchise.animes))
        )
        result = await db.execute(stmt)
        franchise = result.scalar()

        if not franchise:
            raise NotFoundException(f"Franchise {franchise_id} not found")

        return {
            "franchise_id": franchise_id,
            "franchise": franchise,
            "user_id": current_user["id"],
        }


async def valid_anime_for_franchise(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Valida que el anime no tiene franquicia asignada."""
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Anime)
            .where(Anime.id == anime_id, Anime.franchise_id.is_(None))
            .options(selectinload(Anime.franchise))
        )
        result = await db.execute(stmt)
        anime = result.scalar()

        if not anime:
            raise NotFoundException(
                f"Anime {anime_id} not found or already has franchise"
            )

        return {
            "anime_id": anime_id,
            "anime": anime,
            "user_id": current_user["id"],
        }
