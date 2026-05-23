import json
import time
from pathlib import Path

import requests
from ani_scrapy import AnimeAV1Scraper, JKAnimeScraper
from loguru import logger

from config import general_settings
from db import get_episode_franchise_and_season, update_episode_size, update_episode_status
from redis_client import download_lock_key, ordering_lock_key, redis_db, stream_add_event, stream_wait_event

ANIMES_FOLDER = general_settings.ANIMES_FOLDER
MAX_DOWNLOAD_RETRIES = general_settings.MAX_DOWNLOAD_RETRIES

CHUNK_SIZE = 1024 * 1024
MAX_CHUNK_RETRIES = 3
UPDATE_INTERVAL = 1


def _notify_job(job_id: str, state: str, meta: dict) -> None:
    payload = {"job_id": job_id, "state": state, "meta": meta}
    redis_db.publish("job_updates", json.dumps(payload))


def _finalize_franchise_download(franchise_id: str | None) -> None:
    if not franchise_id:
        return
    if redis_db.decr(download_lock_key(franchise_id)) == 0:
        stream_add_event(franchise_id, "downloads_done")


def _server_supports_range(url: str, headers: dict | None = None) -> tuple[bool, int | None]:
    try:
        response = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
        accept_ranges = response.headers.get("Accept-Ranges", "").lower()
        content_length = int(response.headers.get("Content-Length", 0))
        if accept_ranges == "bytes" and content_length > 0:
            return True, content_length
    except Exception as e:
        logger.warning(f"Error checking Range support: {e}")
    return False, None


def _download_file(
    job_id: str,
    anime_id: str,
    franchise_id: str | None,
    season: int,
    episode_number: int,
    download_link: str,
) -> tuple[bool, int | None]:
    """Synchronous download using requests. Returns (success, total_size)."""
    start_time = time.time()
    parsed_season = str(season).zfill(2)
    parsed_ep_number = str(episode_number).zfill(2)

    folder_root = franchise_id if franchise_id else anime_id
    anime_folder = Path(ANIMES_FOLDER) / folder_root / f"Season {parsed_season}"
    anime_folder.mkdir(parents=True, exist_ok=True)
    save_path = anime_folder / f"{anime_id} - S{parsed_season}E{parsed_ep_number}.mp4"

    file_exists = save_path.exists()
    downloaded = save_path.stat().st_size if file_exists else 0
    headers: dict[str, str] = {}
    resume_mode = False

    supports_range, total_size = _server_supports_range(download_link)

    if supports_range and file_exists:
        if downloaded < (total_size or 0):
            resume_mode = True
            headers = {"Range": f"bytes={downloaded}-"}
            logger.debug(f"[{job_id}] Resuming from byte {downloaded}/{total_size}")
        else:
            logger.warning(f"[{job_id}] Local >= remote, redownloading from start")
            save_path.unlink()
            downloaded = 0
    elif not supports_range and not file_exists:
        logger.warning(f"[{job_id}] Server does not support Range, full download required")

    try:
        with requests.get(
            download_link, headers=headers, stream=True, timeout=(10, 300)
        ) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("Content-Length", 0)) + downloaded

            if total_size > 0:
                update_episode_size(anime_id, episode_number, total_size)

            last_update_time = time.time()
            mode = "ab" if resume_mode else "wb"

            with open(save_path, mode) as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if not chunk:
                        continue

                    for attempt in range(MAX_CHUNK_RETRIES):
                        try:
                            f.write(chunk)
                            downloaded += len(chunk)
                            break
                        except Exception as e:
                            logger.error(
                                f"[{job_id}] Chunk failed, attempt {attempt + 1}: {e}"
                            )
                            time.sleep(1)
                    else:
                        raise RuntimeError("Max retries reached for chunk")

                    current_time = time.time()
                    if current_time - last_update_time > UPDATE_INTERVAL:
                        last_update_time = current_time
                        progress = downloaded / total_size * 100 if total_size else 0
                        _notify_job(
                            job_id,
                            "DOWNLOADING",
                            {"size": total_size, "progress": progress},
                        )

        elapsed = time.time() - start_time
        logger.debug(
            f"[{job_id}] Downloaded: {anime_id} "
            f"S{season:02d}E{episode_number:02d} ({total_size} bytes, {elapsed:.1f}s)"
        )
        return True, total_size
    except requests.exceptions.HTTPError as e:
        logger.error(f"[{job_id}] HTTP error downloading {anime_id} E{episode_number}: {e}")
        if e.response is not None and e.response.status_code == 416 and save_path.exists():
            save_path.unlink()
        return False, None
    except Exception as e:
        logger.error(f"[{job_id}] Error downloading {anime_id} E{episode_number}: {e}")
        return False, None


async def _resolve_download_link(job_id: str, anime_id: str, episode_number: int):
    """Tries scrapers in priority order. Returns the download link or None."""
    # Priority 1: AnimeAV1 -> PDrain
    try:
        async with AnimeAV1Scraper(executable_path=general_settings.BRAVE_PATH) as scraper:
            info = await scraper.get_table_download_links(anime_id, episode_number)
            logger.debug(
                f"[{job_id}] AnimeAV1 servers: {[link.server for link in info.download_links]}"
            )
            for link in info.download_links:
                if link.server.lower() != "pdrain":
                    continue
                logger.debug(f"[{job_id}] Trying AnimeAV1/PDrain")
                file_link = await scraper.get_file_download_link(link)
                if file_link:
                    return file_link
    except Exception as e:
        logger.warning(f"[{job_id}] AnimeAV1/PDrain failed: {e}")

    # Priority 2 & 3: JKAnime -> Mediafire / Streamwish (table)
    try:
        async with JKAnimeScraper(executable_path=general_settings.BRAVE_PATH) as scraper:
            info = await scraper.get_table_download_links(anime_id, episode_number)
            logger.debug(
                f"[{job_id}] JKAnime servers: {[link.server for link in info.download_links]}"
            )
            for target in ("mediafire", "streamwish"):
                for link in info.download_links:
                    if link.server.lower() != target:
                        continue
                    logger.debug(f"[{job_id}] Trying JKAnime/{target} (table)")
                    file_link = await scraper.get_file_download_link(link)
                    if file_link:
                        return file_link
    except Exception as e:
        logger.warning(f"[{job_id}] JKAnime (table) failed: {e}")

    # Priority 3: JKAnime -> Streamwish (iframe)
    try:
        async with JKAnimeScraper(executable_path=general_settings.BRAVE_PATH) as scraper:
            logger.debug(f"[{job_id}] Trying JKAnime/Streamwish (iframe)")
            iframe = await scraper.get_iframe_download_links(anime_id, episode_number)
            for link in iframe.download_links:
                if link.server.lower() != "streamwish":
                    continue
                file_link = await scraper.get_file_download_link(link)
                if file_link:
                    return file_link
    except Exception as e:
        logger.warning(f"[{job_id}] JKAnime/Streamwish (iframe) failed: {e}")

    return None


async def download_anime_episode_controller(
    message,
    anime_id: str,
    episode_number: int,
    user_id: str,
) -> None:
    job_id = message.message_id
    retries = message.options.get("retries", 0)
    is_first_try = retries == 0

    with logger.contextualize(user_id=user_id, job_id=job_id):
        info = get_episode_franchise_and_season(anime_id)
        if info is None:
            logger.error(f"Anime {anime_id} not found")
            return
        franchise_id, season = info

        if franchise_id and is_first_try:
            if redis_db.exists(ordering_lock_key(franchise_id)):
                stream_wait_event(franchise_id, "ordering_done")
            redis_db.incr(download_lock_key(franchise_id))

        try:
            update_episode_status(anime_id, episode_number, "GETTING-LINK", job_id=job_id)
            _notify_job(job_id, "GETTING-LINK", {})

            valid_link = await _resolve_download_link(job_id, anime_id, episode_number)
            if not valid_link:
                raise Exception(f"No download link available for {anime_id} E{episode_number}")

            update_episode_status(anime_id, episode_number, "DOWNLOADING")

            success, total_size = _download_file(
                job_id, anime_id, franchise_id, season, episode_number, valid_link,
            )
            if not success:
                raise Exception(f"Download failed for {anime_id} E{episode_number}")

            if total_size is not None:
                update_episode_size(anime_id, episode_number, total_size)

            update_episode_status(anime_id, episode_number, "SUCCESS", job_id=None)
            _notify_job(job_id, "SUCCESS", {})

            _finalize_franchise_download(franchise_id)

        except Exception as e:
            logger.error(f"Error: {e}")

            if retries >= MAX_DOWNLOAD_RETRIES:
                logger.error("Max retries exceeded, marking as FAILED")
                update_episode_status(anime_id, episode_number, "FAILED", job_id=job_id)
                _notify_job(job_id, "FAILED", {})
                _finalize_franchise_download(franchise_id)
                raise

            logger.warning(f"Will retry (attempt {retries + 1}/{MAX_DOWNLOAD_RETRIES})")
            update_episode_status(anime_id, episode_number, "RETRYING")
            _notify_job(job_id, "RETRYING", {"retry_count": retries + 1, "max_retries": MAX_DOWNLOAD_RETRIES})
            raise
