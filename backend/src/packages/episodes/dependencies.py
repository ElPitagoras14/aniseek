from pathlib import Path

from fastapi import Depends

from packages.auth import auth_scheme
from utils.exceptions import ConflictException, NotFoundException

from . import repository
from .config import episodes_settings

ANIMES_FOLDER = Path(episodes_settings.ANIMES_FOLDER)


async def valid_episode_id_public(
    episode_id: int,
    anime_id: str | None = None,
) -> dict:
    """Valida que el episodio existe y retorna los datos necesarios (sin autenticación)."""
    episode = await repository.get_episode_with_anime(episode_id, anime_id)
    if not episode:
        raise NotFoundException(f"Episode {episode_id} not found")

    return {
        "episode_id": episode_id,
        "episode": episode,
        "anime_id": episode["anime_id"],
        "user_id": None,
    }


async def valid_episode_id(
    episode_id: int,
    anime_id: str | None = None,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Valida que el episodio existe y retorna los datos necesarios."""
    episode = await repository.get_episode_with_anime(episode_id, anime_id)
    if not episode:
        raise NotFoundException(f"Episode {episode_id} not found")

    return {
        "episode_id": episode_id,
        "episode": episode,
        "anime_id": episode["anime_id"],
        "user_id": current_user["id"],
    }


async def valid_episode_by_number(
    anime_id: str,
    episode_number: int,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Valida que el episodio existe por número y retorna los datos necesarios."""
    episode = await repository.get_episode_by_anime_and_number(anime_id, episode_number)
    if not episode:
        raise NotFoundException(
            f"Episode {episode_number} not found for anime {anime_id}"
        )

    return {
        "episode_id": episode["id"],
        "episode": episode,
        "anime_id": anime_id,
        "episode_number": episode_number,
        "user_id": current_user["id"],
    }


async def episode_not_downloaded_by_user(
    episode_data: dict = Depends(valid_episode_by_number),
    force_download: bool = False,
) -> dict:
    """Verifica que el episodio NO esté descargado por el usuario (si force_download es False)."""
    if force_download:
        return episode_data

    download = await repository.get_user_episode_download(
        episode_data["user_id"], episode_data["episode_id"]
    )
    if download:
        raise ConflictException("Download already in progress")
    return episode_data


def _resolve_file_path(episode: dict) -> Path:
    franchise_id = episode["anime_franchise_id"]
    parsed_season = str(episode["anime_season"]).zfill(2)
    if franchise_id:
        anime_folder = ANIMES_FOLDER / franchise_id / f"Season {parsed_season}"
    else:
        anime_folder = ANIMES_FOLDER / episode["anime_id"] / f"Season {parsed_season}"

    if not anime_folder.exists():
        raise NotFoundException("Episode file not found")

    parsed_ep_number = str(episode["ep_number"]).zfill(2)
    file_path = (
        anime_folder
        / f"{episode['anime_id']} - S{parsed_season}E{parsed_ep_number}.mp4"
    )
    if not file_path.exists():
        raise NotFoundException("Episode file not found")
    return file_path


async def valid_downloaded_episode(
    episode_data: dict = Depends(valid_episode_id),
) -> dict:
    """Valida que el episodio existe y el archivo físico está disponible."""
    file_path = _resolve_file_path(episode_data["episode"])
    episode_data["file_path"] = str(file_path)
    episode_data["filename"] = (
        f"{episode_data['episode']['anime_id']}-{episode_data['episode']['ep_number']}.mp4"
    )
    return episode_data


async def valid_downloaded_episode_public(
    episode_data: dict = Depends(valid_episode_id_public),
) -> dict:
    """Valida que el episodio existe y el archivo físico está disponible (sin autenticación)."""
    file_path = _resolve_file_path(episode_data["episode"])
    episode_data["file_path"] = str(file_path)
    episode_data["filename"] = (
        f"{episode_data['episode']['anime_id']}-{episode_data['episode']['ep_number']}.mp4"
    )
    return episode_data
