import shutil
import time
from loguru import logger
from sqlalchemy import select, func, distinct
from pathlib import Path

from database import DatabaseSession, Anime, Episode
from redis_client import redis_db
from config import general_settings
from schemas import FranchiseInfo
from utils import (
    get_ordering_key,
    get_download_key,
    stream_add_event,
    stream_wait_event,
)

ANIMES_FOLDER = general_settings.ANIMES_FOLDER


def get_same_anime(anime_id: str, animes: list[dict]):
    for anime in animes:
        if anime["id"] == anime_id:
            return anime
    return None


def get_started_download_count(franchise_id: str):
    with DatabaseSession() as db:
        stmt = (
            select(func.count(distinct(Episode.id)))
            .select_from(Anime)
            .join(Episode)
            .filter(
                Anime.franchise_id == franchise_id,
                Episode.anime_id == Anime.id,
                Episode.status != "PENDING",
                Episode.status != "SUCCESS",
                Episode.status != "FAILED",
            )
        )
        count = db.execute(stmt).scalar_one_or_none()
        return count


def order_franchise_controller(franchise_info: FranchiseInfo):
    start_time = time.time()
    franchise_id = franchise_info["id"]
    logger.debug(f"Starting franchise ordering: {franchise_id}")

    ordering_key = get_ordering_key(franchise_id)
    redis_db.set(ordering_key, 1)

    download_key = get_download_key(franchise_id)
    count = get_started_download_count(franchise_id)
    redis_db.set(download_key, count)

    if count > 0:
        logger.debug(
            f"Waiting for {count} downloads to finish: {franchise_id}"
        )
        stream_wait_event(franchise_id, "downloads_done")

    franchise_folder = Path(ANIMES_FOLDER) / franchise_id
    franchise_folder.mkdir(parents=True, exist_ok=True)

    with DatabaseSession() as db:
        stmt = select(Anime).where(Anime.franchise_id == franchise_id)
        animes = db.execute(stmt).scalars().all()

        for anime in animes:
            anime_id = anime.id
            parsed_season = str(anime.season).zfill(2)
            anime_folder = (
                Path(ANIMES_FOLDER) / anime_id / f"Season {parsed_season}"
            )
            if not anime_folder.exists():
                logger.warning(
                    f"Folder not found: {anime_folder}"
                )
                continue

            same_anime = get_same_anime(anime_id, franchise_info["animes"])
            new_parsed_season = str(same_anime["season"]).zfill(2)

            new_anime_folder = (
                Path(ANIMES_FOLDER)
                / franchise_id
                / f"Season {new_parsed_season}"
            )

            shutil.move(str(anime_folder), str(new_anime_folder))

            old_anime_folder = Path(ANIMES_FOLDER) / anime_id
            old_anime_folder.rmdir()

            anime.season = same_anime["season"]
            db.add(anime)

            for file in new_anime_folder.iterdir():
                new_file_name = file.name.replace(
                    f"S{parsed_season}E",
                    f"S{new_parsed_season}E",
                )
                new_file_path = file.with_name(new_file_name)
                file.rename(new_file_path)

            logger.debug(
                f"Ordered: {anime_id} S{parsed_season} -> S{new_parsed_season}"
            )

    elapsed = time.time() - start_time
    logger.debug(f"Completed ordering: {franchise_id} in {elapsed:.1f}s")

    stream_add_event(franchise_id, "ordering_done")
    redis_db.delete(ordering_key)
