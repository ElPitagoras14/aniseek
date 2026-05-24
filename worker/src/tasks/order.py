import shutil
import time
from pathlib import Path

from loguru import logger

from config import general_settings
from db import get_started_download_count, list_franchise_animes, update_anime_season
from redis_client import (
    download_lock_key,
    ordering_lock_key,
    redis_db,
    stream_add_event,
    stream_wait_event,
)
from schemas import FranchiseInfo

ANIMES_FOLDER = general_settings.ANIMES_FOLDER


def _get_target_season(anime_id: str, animes: list[dict]) -> int | None:
    for a in animes:
        if a["id"] == anime_id:
            return a["season"]
    return None


def _move_anime_folders(
    franchise_id: str,
    anime_id: str,
    old_season: int,
    new_season: int,
) -> None:
    """Physically moves and renames files on disk."""
    old_parsed = str(old_season).zfill(2)
    new_parsed = str(new_season).zfill(2)

    old_folder = Path(ANIMES_FOLDER) / anime_id / f"Season {old_parsed}"
    if not old_folder.exists():
        logger.warning(f"Folder not found: {old_folder}")
        return

    new_folder = Path(ANIMES_FOLDER) / franchise_id / f"Season {new_parsed}"
    shutil.move(str(old_folder), str(new_folder))

    old_root = Path(ANIMES_FOLDER) / anime_id
    if old_root.exists() and not any(old_root.iterdir()):
        old_root.rmdir()

    for file in new_folder.iterdir():
        new_name = file.name.replace(f"S{old_parsed}E", f"S{new_parsed}E")
        file.rename(file.with_name(new_name))


def order_franchise_controller(franchise_info: FranchiseInfo) -> None:
    start_time = time.time()
    franchise_id = franchise_info["id"]
    logger.debug(f"Starting franchise ordering: {franchise_id}")

    ordering_key = ordering_lock_key(franchise_id)
    redis_db.set(ordering_key, 1)

    count = get_started_download_count(franchise_id)
    redis_db.set(download_lock_key(franchise_id), count)

    if count > 0:
        logger.debug(f"Waiting for {count} downloads to finish: {franchise_id}")
        stream_wait_event(franchise_id, "downloads_done")

    try:
        franchise_folder = Path(ANIMES_FOLDER) / franchise_id
        franchise_folder.mkdir(parents=True, exist_ok=True)

        animes = list_franchise_animes(franchise_id)
        for anime in animes:
            anime_id = anime["id"]
            old_season = anime["season"]
            new_season = _get_target_season(anime_id, franchise_info["animes"])
            if new_season is None:
                logger.warning(f"No target season provided for {anime_id}")
                continue

            _move_anime_folders(franchise_id, anime_id, old_season, new_season)
            update_anime_season(anime_id, new_season)
            logger.debug(f"Ordered: {anime_id} S{old_season:02d} -> S{new_season:02d}")

        elapsed = time.time() - start_time
        logger.debug(f"Completed ordering: {franchise_id} in {elapsed:.1f}s")

        stream_add_event(franchise_id, "ordering_done")
    except Exception as e:
        logger.error(f"Franchise ordering failed for {franchise_id}: {e}")
        raise
    finally:
        redis_db.delete(ordering_key)
