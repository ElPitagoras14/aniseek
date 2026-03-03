from pathlib import Path

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from packages.auth import auth_scheme
from utils.exceptions import NotFoundException, ConflictException
from databases.postgres import (
    AsyncDatabaseSession,
    Anime,
    Episode,
    UserSaveAnime,
    UserDownloadEpisode,
)
from .config import anime_settings


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

        from datetime import datetime, timezone, timedelta

        current_time = datetime.now(timezone.utc)
        last_scraped = anime.last_scraped_at.replace(tzinfo=timezone.utc)
        cooldown_minutes = 5

        time_diff = current_time - last_scraped
        if time_diff < timedelta(minutes=cooldown_minutes):
            remaining_seconds = int(
                (
                    timedelta(minutes=cooldown_minutes) - time_diff
                ).total_seconds()
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


async def valid_episode_id_public(
    episode_id: int,
    anime_id: str | None = None,
) -> dict:
    """Valida que el episodio existe y retorna los datos necesarios (sin autenticación)."""
    async with AsyncDatabaseSession() as db:
        stmt = select(Episode).where(Episode.id == episode_id)
        if anime_id:
            stmt = stmt.where(Episode.anime_id == anime_id)
        stmt = stmt.options(selectinload(Episode.anime))

        result = await db.execute(stmt)
        episode = result.scalar()

        if not episode:
            raise NotFoundException(f"Episode {episode_id} not found")

        return {
            "episode_id": episode_id,
            "episode": episode,
            "anime_id": episode.anime_id,
            "user_id": None,
        }


async def valid_episode_id(
    episode_id: int,
    anime_id: str | None = None,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Valida que el episodio existe y retorna los datos necesarios."""
    async with AsyncDatabaseSession() as db:
        stmt = select(Episode).where(Episode.id == episode_id)
        if anime_id:
            stmt = stmt.where(Episode.anime_id == anime_id)
        stmt = stmt.options(selectinload(Episode.anime))

        result = await db.execute(stmt)
        episode = result.scalar()

        if not episode:
            raise NotFoundException(f"Episode {episode_id} not found")

        return {
            "episode_id": episode_id,
            "episode": episode,
            "anime_id": episode.anime_id,
            "user_id": current_user["id"],
        }


async def valid_episode_by_number(
    anime_id: str,
    episode_number: int,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Valida que el episodio existe por número y retorna los datos necesarios."""
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Episode)
            .where(
                Episode.anime_id == anime_id,
                Episode.ep_number == episode_number,
            )
            .options(selectinload(Episode.anime))
        )
        result = await db.execute(stmt)
        episode = result.scalar()

        if not episode:
            raise NotFoundException(
                f"Episode {episode_number} not found for anime {anime_id}"
            )

        return {
            "episode_id": episode.id,
            "episode": episode,
            "anime_id": anime_id,
            "episode_number": episode_number,
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


async def episode_not_downloaded_by_user(
    episode_data: dict = Depends(valid_episode_by_number),
    force_download: bool = False,
) -> dict:
    """Verifica que el episodio NO esté descargado por el usuario (si force_download es False)."""
    if force_download:
        return episode_data

    async with AsyncDatabaseSession() as db:
        stmt = select(UserDownloadEpisode).where(
            UserDownloadEpisode.user_id == episode_data["user_id"],
            UserDownloadEpisode.episode_id == episode_data["episode_id"],
        )
        result = await db.execute(stmt)
        download = result.scalar()

        if download:
            raise ConflictException("Download already in progress")

    return episode_data


ANIMES_FOLDER = Path(anime_settings.ANIMES_FOLDER)


async def valid_downloaded_episode(
    episode_data: dict = Depends(valid_episode_id),
) -> dict:
    """Valida que el episodio existe y el archivo físico está disponible."""
    episode = episode_data["episode"]

    franchise_id = episode.anime.franchise_id
    parsed_season = str(episode.anime.season).zfill(2)
    anime_folder = ANIMES_FOLDER / episode.anime_id / f"Season {parsed_season}"

    if franchise_id:
        anime_folder = ANIMES_FOLDER / franchise_id / f"Season {parsed_season}"

    if not anime_folder.exists():
        raise NotFoundException("Episode file not found")

    parsed_ep_number = str(episode.ep_number).zfill(2)
    file_path = (
        anime_folder
        / f"{episode.anime_id} - S{parsed_season}E{parsed_ep_number}.mp4"
    )

    if not file_path.exists():
        raise NotFoundException("Episode file not found")

    episode_data["file_path"] = str(file_path)
    episode_data["filename"] = f"{episode.anime_id}-{episode.ep_number}.mp4"

    return episode_data


async def valid_downloaded_episode_public(
    episode_data: dict = Depends(valid_episode_id_public),
) -> dict:
    """Valida que el episodio existe y el archivo físico está disponible (sin autenticación)."""
    episode = episode_data["episode"]

    franchise_id = episode.anime.franchise_id
    parsed_season = str(episode.anime.season).zfill(2)
    anime_folder = ANIMES_FOLDER / episode.anime_id / f"Season {parsed_season}"

    if franchise_id:
        anime_folder = ANIMES_FOLDER / franchise_id / f"Season {parsed_season}"

    if not anime_folder.exists():
        raise NotFoundException("Episode file not found")

    parsed_ep_number = str(episode.ep_number).zfill(2)
    file_path = (
        anime_folder
        / f"{episode.anime_id} - S{parsed_season}E{parsed_ep_number}.mp4"
    )

    if not file_path.exists():
        raise NotFoundException("Episode file not found")

    episode_data["file_path"] = str(file_path)
    episode_data["filename"] = f"{episode.anime_id}-{episode.ep_number}.mp4"

    return episode_data
