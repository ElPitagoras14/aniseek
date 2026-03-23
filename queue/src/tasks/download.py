import json
from pathlib import Path
import time
from loguru import logger
import requests
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ani_scrapy import JKAnimeScraper, AnimeAV1Scraper
from database import DatabaseSession, Anime, Episode
from redis_client import redis_db
from config import general_settings
from utils import (
    get_ordering_key,
    get_download_key,
    stream_add_event,
    stream_wait_event,
)

ANIMES_FOLDER = general_settings.ANIMES_FOLDER
MAX_DOWNLOAD_RETRIES = general_settings.MAX_DOWNLOAD_RETRIES
RETRY_DOWNLOAD_INTERVAL = general_settings.RETRY_DOWNLOAD_INTERVAL

CHUNK_SIZE = 1024 * 1024
MAX_CHUNK_RETRIES = 3
UPDATE_INTERVAL = 1


def server_supports_range(url, headers=None):
    try:
        response = requests.head(
            url, headers=headers, allow_redirects=True, timeout=10
        )
        accept_ranges = response.headers.get("Accept-Ranges", "").lower()
        content_length = int(response.headers.get("Content-Length", 0))
        if accept_ranges == "bytes" and content_length > 0:
            return True, content_length
    except Exception as e:
        logger.warning(f"Error checking Range support: {e}")
    return False, None


def update_episode_status(
    anime_id: str, episode_number: int, status: str, job_id: str = None
):
    with DatabaseSession() as db:
        stmt = select(Episode).filter_by(
            anime_id=anime_id, ep_number=episode_number
        )
        episode = db.execute(stmt).scalar_one_or_none()
        if not episode:
            logger.error(
                f"[{job_id}] Episode {anime_id} - {episode_number} not found"
            )
            return
        episode.status = status
        if job_id is not None:
            episode.job_id = job_id
        db.add(episode)


def notify_job(job_id: str, state: str, meta: dict):
    payload = {
        "job_id": job_id,
        "state": state,
        "meta": meta,
    }
    redis_db.publish("job_updates", json.dumps(payload))


def get_anime_episode_franchise(anime_id: str):
    with DatabaseSession() as db:
        stmt = select(Anime).filter(Anime.id == anime_id)
        anime = db.execute(stmt).scalar_one_or_none()
        return anime.franchise_id


def download_episode(
    job_id: str,
    anime_id: str,
    season: int,
    episode_number: int,
    download_link: str,
    server: str,
):
    start_time = time.time()
    logger.debug(
        f"[{job_id}] Starting download: {anime_id} S{season:02d}E{episode_number:02d} from {server}"
    )

    try:
        parsed_season = str(season).zfill(2)
        parsed_ep_number = str(episode_number).zfill(2)

        franchise_id = None
        with DatabaseSession() as db:
            stmt = select(Anime).where(Anime.id == anime_id)
            anime = db.execute(stmt).scalar_one()
            franchise_id = anime.franchise_id

        anime_folder = (
            Path(ANIMES_FOLDER) / anime_id / f"Season {parsed_season}"
        )
        if franchise_id:
            anime_folder = (
                Path(ANIMES_FOLDER) / franchise_id / f"Season {parsed_season}"
            )
        anime_folder.mkdir(parents=True, exist_ok=True)

        save_path = (
            anime_folder
            / f"{anime_id} - S{parsed_season}E{parsed_ep_number}.mp4"
        )

        file_exists = save_path.exists()
        downloaded = save_path.stat().st_size if file_exists else 0
        headers = {}

        resume_mode = False

        supports_range, total_size = server_supports_range(download_link)

        if supports_range and file_exists:
            if downloaded < total_size:
                resume_mode = True
                headers = {"Range": f"bytes={downloaded}-"}
                logger.debug(
                    f"[{job_id}] Resuming from byte {downloaded}/{total_size}"
                )
            else:
                logger.warning(
                    f"[{job_id}] Local >= remote, redownloading from start"
                )
                save_path.unlink()
                downloaded = 0
        elif not supports_range and not file_exists:
            logger.warning(
                f"[{job_id}] Server does not support Range, full download required"
            )

        with requests.get(
            download_link, headers=headers, stream=True, timeout=(10, 300)
        ) as response:
            response.raise_for_status()
            total_size = (
                int(response.headers.get("Content-Length", 0)) + downloaded
            )

            last_update_time = time.time()
            mode = "ab" if resume_mode else "wb"

            with open(save_path, mode) as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if not chunk:
                        continue

                    for attemp in range(MAX_CHUNK_RETRIES):
                        try:
                            f.write(chunk)
                            downloaded += len(chunk)
                            break
                        except Exception as e:
                            logger.error(
                                f"[{job_id}] Chunk failed, attempt {attemp + 1}: {e}"
                            )
                            time.sleep(1)
                    else:
                        raise RuntimeError("Max retries reached for chunk")

                    current_time = time.time()
                    if current_time - last_update_time > UPDATE_INTERVAL:
                        last_update_time = current_time
                        progress = downloaded / total_size * 100
                        notify_job(
                            job_id,
                            "DOWNLOADING",
                            {"total": total_size, "progress": progress},
                        )

        with DatabaseSession() as db:
            stmt = (
                select(Episode)
                .where(
                    Episode.anime_id == anime_id,
                    Episode.ep_number == episode_number,
                )
                .options(selectinload(Episode.anime))
            )
            episode = db.execute(stmt).scalar_one()
            episode.size = total_size
            db.add(episode)

        elapsed = time.time() - start_time
        logger.debug(
            f"[{job_id}] Downloaded: {anime_id} S{season:02d}E{episode_number:02d} ({total_size} bytes, {elapsed:.1f}s)"
        )
        return True
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"[{job_id}] HTTP error downloading {anime_id} E{episode_number}: {e}"
        )
        if e.response.status_code == 416 and save_path.exists():
            save_path.unlink()
        return False
    except Exception as e:
        logger.error(
            f"[{job_id}] Error downloading {anime_id} E{episode_number}: {e}"
        )
        return False


async def download_anime_episode_controller(
    message,
    anime_id: str,
    episode_number: int,
    user_id: str,
):
    job_id = message.message_id
    retry_count = message.options.get("retry_count", 0)

    is_firt_try = retry_count == 0
    franchise_id = get_anime_episode_franchise(anime_id)

    if franchise_id and is_firt_try:
        ordering_key = get_ordering_key(franchise_id)
        if redis_db.exists(ordering_key):
            stream_wait_event(franchise_id, "ordering_done")
        redis_db.incr(get_download_key(franchise_id))

    try:
        update_episode_status(anime_id, episode_number, "GETTING-LINK", job_id)
        notify_job(job_id, "GETTING-LINK", {})

        season = 1
        with DatabaseSession() as db:
            stmt = select(Anime).where(Anime.id == anime_id)
            anime = db.execute(stmt).scalar_one()
            season = anime.season

        valid_download_link = None
        selected_download_info = None

        # Priority 1: AnimeAV1 -> PDrain -> table
        try:
            async with AnimeAV1Scraper(
                executable_path=general_settings.BRAVE_PATH
            ) as scraper:
                download_info = await scraper.get_table_download_links(
                    anime_id, episode_number
                )
                download_links = download_info.download_links

                logger.debug(
                    f"[{job_id}] AnimeAV1 returned servers: "
                    f"{[link.server for link in download_links]}"
                )

                pdrain_links = [
                    link
                    for link in download_links
                    if link.server.lower() == "pdrain"
                ]

                for link in pdrain_links:
                    logger.debug(f"[{job_id}] Trying AnimeAV1/PDrain")
                    file_download_link = await scraper.get_file_download_link(
                        link
                    )
                    if file_download_link:
                        valid_download_link = file_download_link
                        selected_download_info = link
                        break
        except Exception as e:
            logger.warning(f"[{job_id}] AnimeAV1/PDrain failed: {e}")

        # Priority 2 & 3: JKAnime -> Mediafire/Streamwish -> table
        if not valid_download_link:
            try:
                async with JKAnimeScraper(
                    executable_path=general_settings.BRAVE_PATH
                ) as scraper:
                    download_info = await scraper.get_table_download_links(
                        anime_id, episode_number
                    )
                    download_links = download_info.download_links

                    logger.debug(
                        f"[{job_id}] JKAnime returned servers: "
                        f"{[link.server for link in download_links]}"
                    )

                    mediafire_links = [
                        link
                        for link in download_links
                        if link.server.lower() == "mediafire"
                    ]

                    for link in mediafire_links:
                        logger.debug(f"[{job_id}] Trying JKAnime/Mediafire")
                        file_download_link = (
                            await scraper.get_file_download_link(link)
                        )
                        if file_download_link:
                            valid_download_link = file_download_link
                            selected_download_info = link
                            break

                    streamwish_links = [
                        link
                        for link in download_links
                        if link.server.lower() == "streamwish"
                    ]

                    for link in streamwish_links:
                        logger.debug(
                            f"[{job_id}] Trying JKAnime/Streamwish (table)"
                        )
                        file_download_link = (
                            await scraper.get_file_download_link(link)
                        )
                        if file_download_link:
                            valid_download_link = file_download_link
                            selected_download_info = link
                            break
            except Exception as e:
                logger.warning(f"[{job_id}] JKAnime failed: {e}")

        # Priority 4: JKAnime -> Streamwish -> iframe
        if not valid_download_link:
            try:
                async with JKAnimeScraper(
                    executable_path=general_settings.BRAVE_PATH
                ) as scraper:
                    logger.debug(
                        f"[{job_id}] Trying JKAnime/Streamwish (iframe)"
                    )
                    iframe_download_links = (
                        await scraper.get_iframe_download_links(
                            anime_id, episode_number
                        )
                    )
                    for link in iframe_download_links.download_links:
                        if link.server != "Streamwish":
                            continue
                        file_download_link = (
                            await scraper.get_file_download_link(link)
                        )
                        if file_download_link:
                            valid_download_link = file_download_link
                            selected_download_info = link
                            break
            except Exception as e:
                logger.warning(
                    f"[{job_id}] JKAnime/Streamwish (iframe) failed: {e}"
                )

        if not valid_download_link:
            raise Exception(
                f"No download link available for {anime_id} E{episode_number}"
            )

        update_episode_status(anime_id, episode_number, "DOWNLOADING")
        notify_job(job_id, "DOWNLOADING", {})

        download_status = download_episode(
            job_id,
            anime_id,
            season,
            episode_number,
            valid_download_link,
            selected_download_info.server,
        )

        if not download_status:
            raise Exception(
                f"Download failed for {anime_id} E{episode_number}"
            )

        update_episode_status(anime_id, episode_number, "SUCCESS", None)
        notify_job(job_id, "SUCCESS", {})

        if franchise_id:
            count = redis_db.decr(get_download_key(franchise_id))
            if count == 0:
                stream_add_event(franchise_id, "downloads_done")

    except Exception as e:
        logger.error(f"[{job_id}] Error: {e}")

        if retry_count >= MAX_DOWNLOAD_RETRIES:
            logger.error(f"[{job_id}] Max retries exceeded")
            update_episode_status(anime_id, episode_number, "FAILED", job_id)
            notify_job(job_id, "FAILED", {})
            if franchise_id:
                count = redis_db.decr(get_download_key(franchise_id))
                if count == 0:
                    stream_add_event(franchise_id, "downloads_done")
            raise e

        logger.warning(
            f"[{job_id}] Retrying (attempt {retry_count + 1}/{MAX_DOWNLOAD_RETRIES})"
        )
        update_episode_status(anime_id, episode_number, "RETRYING")
        notify_job(
            job_id,
            "RETRYING",
            {
                "retry_count": retry_count + 1,
                "max_retries": MAX_DOWNLOAD_RETRIES,
            },
        )
        raise e
