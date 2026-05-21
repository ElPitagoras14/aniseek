from fastapi import Depends
from sqlalchemy import select

from databases.postgres import (
    Anime,
    AsyncDatabaseSession,
    UserSaveAnime,
)
from packages.auth import auth_scheme
from utils.exceptions import ConflictException, NotFoundException


async def valid_anime_for_update(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Valida que el anime existe y puede ser actualizado (cooldown 5 min)."""
    async with AsyncDatabaseSession() as db:
        stmt = select(Anime).where(Anime.id == anime_id)
        anime = await db.scalar(stmt)

        if not anime or not anime.last_scraped_at:
            raise NotFoundException(
                "Anime not found or not yet created. "
                "Use GET /animes/info/{anime_id} to create it first."
            )

        from datetime import datetime, timedelta, timezone

        current_time = datetime.now(timezone.utc)
        last_scraped = anime.last_scraped_at.replace(tzinfo=timezone.utc)
        cooldown_minutes = 5

        time_diff = current_time - last_scraped
        if time_diff < timedelta(minutes=cooldown_minutes):
            remaining_seconds = int(
                (timedelta(minutes=cooldown_minutes) - time_diff).total_seconds()
            )
            raise NotFoundException(
                f"Anime was updated recently. "
                f"Please wait {remaining_seconds} seconds before updating."
            )

        return {
            "anime_id": anime_id,
            "user_id": current_user["id"],
            "anime_db": anime,
        }


async def valid_anime_id(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Valida que el anime existe y retorna los datos necesarios."""
    async with AsyncDatabaseSession() as db:
        stmt = select(Anime).where(Anime.id == anime_id)
        result = await db.execute(stmt)
        anime = result.scalar()

        if not anime:
            raise NotFoundException(f"Anime {anime_id} not found")

        return {
            "anime_id": anime_id,
            "anime": anime,
            "user_id": current_user["id"],
        }


async def anime_is_saved_by_user(
    anime_data: dict = Depends(valid_anime_id),
) -> dict:
    """Verifica que el usuario tenga el anime guardado."""
    async with AsyncDatabaseSession() as db:
        stmt = select(UserSaveAnime).where(
            UserSaveAnime.user_id == anime_data["user_id"],
            UserSaveAnime.anime_id == anime_data["anime_id"],
        )
        result = await db.execute(stmt)
        saved_anime = result.scalar()

        if not saved_anime:
            raise NotFoundException("Anime not saved by user")

        return anime_data


async def anime_not_saved_by_user(
    anime_data: dict = Depends(valid_anime_id),
) -> dict:
    """Verifica que el usuario NO tenga el anime guardado."""
    async with AsyncDatabaseSession() as db:
        stmt = select(UserSaveAnime).where(
            UserSaveAnime.user_id == anime_data["user_id"],
            UserSaveAnime.anime_id == anime_data["anime_id"],
        )
        result = await db.execute(stmt)
        saved_anime = result.scalar()

        if saved_anime:
            raise ConflictException("Anime already saved by user")

        return anime_data


async def user_not_saved_anime(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Verifica que el usuario NO tenga el anime guardado (sin requerir que el anime exista en DB)."""
    async with AsyncDatabaseSession() as db:
        stmt = select(UserSaveAnime).where(
            UserSaveAnime.user_id == current_user["id"],
            UserSaveAnime.anime_id == anime_id,
        )
        result = await db.execute(stmt)
        saved_anime = result.scalar()

        if saved_anime:
            raise ConflictException("Anime already saved by user")

    return {
        "anime_id": anime_id,
        "user_id": current_user["id"],
    }


