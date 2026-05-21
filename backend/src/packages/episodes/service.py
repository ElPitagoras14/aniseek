import shutil
from pathlib import Path

from loguru import logger

from database.client import db
from utils.exceptions import ConflictException, NotFoundException
from worker import download_anime_episode

from . import repository
from .config import episodes_settings
from .utils import (
    cast_animes_storage_list,
    cast_download_task_list,
    cast_downloaded_anime_list,
    cast_episode_download_list,
    cast_job_id,
)

ANIMES_FOLDER = Path(episodes_settings.ANIMES_FOLDER)


def is_folder_empty(folder: Path) -> bool:
    return not any(folder.iterdir())


def _build_download_dict(row: dict) -> dict:
    return {
        "id": row["episode_id"],
        "anime_id": row["anime_id"],
        "title": row["title"],
        "episode_number": row["episode_number"],
        "poster": row["poster"],
        "job_id": row["job_id"],
        "size": row["size"],
        "status": row["status"],
        "downloaded_at": row["downloaded_at"],
    }


async def get_download_episodes_controller(
    user_id: str, anime_id: str | None = None, limit: int = 10, page: int = 1
) -> dict:
    logger.debug("Getting downloads")
    count, rows = await repository.list_user_downloads(user_id, anime_id, limit, page)
    episode_downloads = [_build_download_dict(r) for r in rows]
    return cast_episode_download_list(episode_downloads, count)


async def get_last_downloaded_episodes_controller(user_id: str) -> dict:
    logger.debug("Getting last downloaded episodes")
    rows = await repository.list_last_user_downloads(user_id, limit=5)
    episodes = [_build_download_dict(r) for r in rows]
    return cast_episode_download_list(episodes, len(episodes))


async def get_downloaded_animes_controller(user_id: str) -> dict:
    logger.debug("Getting downloaded animes")
    animes = await repository.list_user_downloaded_animes(user_id)
    animes_info = [{"id": a["id"], "title": a["title"]} for a in animes]
    return cast_downloaded_anime_list(animes_info, len(animes_info))


async def download_anime_episode_controller(
    episode_id: int, force_download: bool, user_id: str
) -> str:
    logger.debug(f"Downloading episode with id: {episode_id}")
    episode = await repository.get_episode_with_anime(episode_id)
    if not episode:
        raise NotFoundException("Episode not found")

    anime_id = episode["anime_id"]
    episode_number = episode["ep_number"]

    user_download = await repository.get_user_episode_download(user_id, episode_id)
    if user_download and not force_download:
        raise ConflictException("Download already in progress")

    any_download = await repository.get_any_episode_download_with_job(episode_id)
    if any_download and not force_download:
        return cast_job_id(any_download["job_id"])

    result = download_anime_episode.send(anime_id, episode_number, user_id)

    async with db.transaction():
        if not force_download:
            await repository.insert_user_episode_download(user_id, episode_id)
        await repository.update_episode_job(episode_id, result.message_id, "PENDING")

    logger.debug(f"Enqueued download with job id: {result.message_id}")
    return cast_job_id(result.message_id)


async def delete_download_episode_controller(episode_id: int, user_id: str) -> str:
    logger.debug(f"Deleting download episode with id: {episode_id}")
    episode = await repository.get_episode_with_anime(episode_id)
    if not episode:
        raise NotFoundException("Episode not found")

    user_download = await repository.get_user_episode_download(user_id, episode_id)
    if not user_download:
        raise NotFoundException("Download not found")

    await repository.delete_user_episode_download(user_id, episode_id)

    users_downloads = await repository.count_episode_downloads(episode_id)
    if users_downloads == 0:
        parsed_season = str(episode["anime_season"]).zfill(2)
        franchise_id = episode["anime_franchise_id"]
        if franchise_id:
            anime_folder = ANIMES_FOLDER / franchise_id / f"Season {parsed_season}"
        else:
            anime_folder = ANIMES_FOLDER / episode["anime_id"] / f"Season {parsed_season}"

        if not anime_folder.exists():
            raise NotFoundException("Episode file not found")

        ep_number = str(episode["ep_number"]).zfill(2)
        file_path = (
            anime_folder / f"{episode['anime_id']} - S{parsed_season}E{ep_number}.mp4"
        )
        if file_path.exists():
            file_path.unlink()

        if is_folder_empty(anime_folder):
            shutil.rmtree(anime_folder)
            logger.debug(f"Deleted folder: {anime_folder}")
            if not franchise_id:
                anime_root_folder = ANIMES_FOLDER / episode["anime_id"]
                if anime_root_folder.exists() and is_folder_empty(anime_root_folder):
                    shutil.rmtree(anime_root_folder)
                    logger.debug(f"Deleted anime root folder: {anime_root_folder}")

    logger.debug(f"Deleted download episode with id: {episode_id}")
    return "Episode deleted successfully"


async def download_anime_episode_bulk_controller(
    anime_id: str, episode_numbers: list[int], user_id: str
) -> dict:
    logger.debug(f"Downloading anime with id: {anime_id}")
    success_enqueued = []
    failed_enqueued = []

    for ep_number in episode_numbers:
        try:
            episode = await repository.get_episode_by_anime_and_number(
                anime_id, ep_number
            )
            if not episode:
                raise NotFoundException("Episode not found")

            existing = await repository.get_user_episode_download(
                user_id, episode["id"]
            )
            if existing:
                logger.warning(
                    f"Episode {episode['id']} already enqueued for user {user_id}"
                )
                failed_enqueued.append([None, ep_number])
                continue

            result = download_anime_episode.send(anime_id, episode["ep_number"], user_id)
            logger.debug(f"Enqueued download with job id: {result.message_id}")

            async with db.transaction():
                await repository.insert_user_episode_download(user_id, episode["id"])
                await repository.update_episode_job(
                    episode["id"], result.message_id, "PENDING"
                )

            success_enqueued.append([result.message_id, ep_number])
        except Exception as e:
            logger.error(f"Error downloading episode: {e}")
            failed_enqueued.append([None, ep_number])

    parsed_data = [
        {"job_id": s[0], "episode_number": s[1], "success": True}
        for s in success_enqueued
    ] + [
        {"job_id": f[0], "episode_number": f[1], "success": False}
        for f in failed_enqueued
    ]
    return cast_download_task_list(parsed_data, len(parsed_data))


async def get_animes_storage_controller(limit: int = 10, page: int = 1) -> dict:
    logger.info("Getting animes storage controller")
    offset = (page - 1) * limit
    count, rows = await repository.list_animes_storage(limit, offset)
    logger.debug(f"Found {count} animes")

    animes_info = [
        {"id": r["id"], "title": r["title"], "size": r["size"]} for r in rows
    ]
    return cast_animes_storage_list(animes_info, count)


async def delete_anime_storage_controller(anime_id: str, user_id: str) -> str:
    logger.debug(f"Deleting anime with id: {anime_id}")
    anime = await repository.get_anime_with_episodes_for_storage(anime_id)
    if not anime:
        raise NotFoundException("Anime not found")

    episode_ids = [ep["id"] for ep in anime["episodes"]]

    async with db.transaction():
        await repository.delete_user_downloads_for_episodes(episode_ids)
        await repository.reset_episodes_storage(anime_id)

    logger.debug("Reset episode sizes and job ids")

    franchise_id = anime["franchise_id"]
    parsed_season = str(anime["season"]).zfill(2)

    if franchise_id:
        anime_folder = ANIMES_FOLDER / franchise_id / f"Season {parsed_season}"
    else:
        anime_folder = ANIMES_FOLDER / anime_id

    for episode in anime["episodes"]:
        parsed_ep_number = str(episode["ep_number"]).zfill(2)
        file_path = (
            anime_folder / f"{anime['id']} - S{parsed_season}E{parsed_ep_number}.mp4"
        )
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Deleted file: {file_path}")

    if anime_folder.exists() and is_folder_empty(anime_folder):
        shutil.rmtree(anime_folder)
        logger.debug(f"Deleted folder: {anime_folder}")

    return "Anime storage deleted successfully"
