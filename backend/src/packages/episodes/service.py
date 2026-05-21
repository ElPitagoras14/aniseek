import shutil
from pathlib import Path

from loguru import logger
from sqlalchemy import delete, desc, func, select, update
from sqlalchemy.orm import selectinload

from databases.postgres import (
    Anime,
    AsyncDatabaseSession,
    Episode,
    UserDownloadEpisode,
)
from utils.exceptions import ConflictException, NotFoundException
from worker import download_anime_episode

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


async def get_download_episodes_controller(
    user_id: str, anime_id: str | None = None, limit: int = 10, page: int = 1
) -> tuple[int, dict]:
    logger.debug("Getting downloads")

    async with AsyncDatabaseSession() as db:
        stmt = (
            select(UserDownloadEpisode)
            .where(UserDownloadEpisode.user_id == user_id)
            .options(
                selectinload(UserDownloadEpisode.episode).selectinload(Episode.anime),
            )
        )

        if anime_id:
            stmt = (
                stmt.join(UserDownloadEpisode.episode)
                .join(Episode.anime)
                .filter(Anime.id == anime_id)
            )

        result_count = await db.execute(stmt)
        count = len(result_count.scalars().all())

        stmt = (
            stmt.order_by(desc(UserDownloadEpisode.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await db.execute(stmt)
        downloads = result.scalars().all()

        episode_downloads = [
            {
                "id": episode.episode_id,
                "anime_id": episode.episode.anime_id,
                "title": episode.episode.anime.title,
                "episode_number": episode.episode.ep_number,
                "poster": episode.episode.anime.poster,
                "job_id": episode.episode.job_id,
                "size": episode.episode.size,
                "status": episode.episode.status,
                "downloaded_at": episode.created_at,
            }
            for episode in downloads
        ]

        casted_episode_downloads = cast_episode_download_list(episode_downloads, count)

    return casted_episode_downloads


async def get_last_downloaded_episodes_controller(
    user_id: str,
) -> dict:
    logger.debug("Getting last downloaded episodes")
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(UserDownloadEpisode)
            .where(UserDownloadEpisode.user_id == user_id)
            .options(
                selectinload(UserDownloadEpisode.episode).selectinload(Episode.anime),
            )
            .order_by(desc(UserDownloadEpisode.created_at))
            .limit(5)
        )
        result = await db.execute(stmt)
        episodes = result.scalars().all()
        episodes = [
            {
                "id": episode.episode_id,
                "anime_id": episode.episode.anime_id,
                "title": episode.episode.anime.title,
                "episode_number": episode.episode.ep_number,
                "poster": episode.episode.anime.poster,
                "job_id": episode.episode.job_id,
                "size": episode.episode.size,
                "status": episode.episode.status,
                "downloaded_at": episode.created_at,
            }
            for episode in episodes
        ]
        casted_episodes = cast_episode_download_list(episodes, len(episodes))

        return casted_episodes


async def get_downloaded_animes_controller(user_id: str) -> dict:
    logger.debug("Getting downloaded animes")

    async with AsyncDatabaseSession() as db:
        stmt = (
            select(UserDownloadEpisode)
            .where(UserDownloadEpisode.user_id == user_id)
            .options(
                selectinload(UserDownloadEpisode.episode),
            )
        )
        result = await db.execute(stmt)
        episode_downloads = result.scalars().all()
        anime_ids = [
            episode_download.episode.anime_id for episode_download in episode_downloads
        ]

        stmt = select(Anime).where(Anime.id.in_(anime_ids))
        result = await db.execute(stmt)
        animes = result.scalars().all()
        animes_info = [
            {
                "id": anime.id,
                "title": anime.title,
            }
            for anime in animes
        ]

        casted_animes = cast_downloaded_anime_list(animes_info, len(animes))
        return casted_animes


async def download_anime_episode_controller(
    episode_id: int,
    force_download: bool,
    user_id: str,
) -> str:
    logger.debug(f"Downloading episode with id: {episode_id}")

    async with AsyncDatabaseSession() as db:
        stmt = select(Episode).where(Episode.id == episode_id)
        episode = await db.scalar(stmt)

        anime_id = episode.anime_id
        episode_number = episode.ep_number

        stmt = select(UserDownloadEpisode).where(
            UserDownloadEpisode.user_id == user_id,
            UserDownloadEpisode.episode_id == episode.id,
        )
        download = await db.scalar(stmt)
        if download and not force_download:
            raise ConflictException("Download already in progress")

        stmt = select(UserDownloadEpisode).where(
            UserDownloadEpisode.episode_id == episode.id,
        )
        general_download = await db.scalar(stmt)
        if general_download and not force_download:
            return cast_job_id(general_download.episode.job_id)

        result = download_anime_episode.send(anime_id, episode_number, user_id)

        if not force_download:
            new_download = UserDownloadEpisode(
                user_id=user_id,
                episode_id=episode.id,
            )
            db.add(new_download)

        episode.job_id = result.message_id
        episode.status = "PENDING"
        db.add(episode)

        logger.debug(f"Enqueued download with job id: {result.message_id}")

        return cast_job_id(result.message_id)


async def delete_download_episode_controller(episode_id: int, user_id: str) -> str:
    logger.debug(f"Deleting download episode with id: {episode_id}")
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Episode)
            .where(Episode.id == episode_id)
            .options(selectinload(Episode.anime))
        )
        result = await db.execute(stmt)
        episode = result.scalar()

        stmt = select(UserDownloadEpisode).where(
            UserDownloadEpisode.episode_id == episode.id,
            UserDownloadEpisode.user_id == user_id,
        )
        result = await db.execute(stmt)
        download = result.scalar()
        if not download:
            raise NotFoundException("Download not found")

        await db.delete(download)
        await db.flush()

        stmt = (
            select(func.count())
            .select_from(UserDownloadEpisode)
            .where(UserDownloadEpisode.episode_id == episode.id)
        )
        result_count = await db.execute(stmt)
        users_downloads = result_count.scalar_one()

        if users_downloads == 0:
            parsed_season = str(episode.anime.season).zfill(2)
            franchise_id = episode.anime.franchise_id
            anime_folder = ANIMES_FOLDER / episode.anime_id / f"Season {parsed_season}"
            if franchise_id:
                anime_folder = ANIMES_FOLDER / franchise_id / f"Season {parsed_season}"
            if not anime_folder.exists():
                raise NotFoundException("Episode file not found")

            ep_number = str(episode.ep_number).zfill(2)
            file_path = (
                anime_folder / f"{episode.anime_id} - S{parsed_season}E{ep_number}.mp4"
            )
            if file_path.exists():
                file_path.unlink()

            if is_folder_empty(anime_folder):
                shutil.rmtree(anime_folder)
                logger.debug(f"Deleted folder: {anime_folder}")
                if not franchise_id:
                    anime_root_folder = ANIMES_FOLDER / episode.anime_id
                    if anime_root_folder.exists() and is_folder_empty(
                        anime_root_folder
                    ):
                        shutil.rmtree(anime_root_folder)
                        logger.debug(f"Deleted anime root folder: {anime_root_folder}")

        logger.debug(f"Deleted download episode with id: {episode_id}")

        return "Episode deleted successfully"


async def download_anime_episode_bulk_controller(
    anime_id: str, episode_numbers: list[int], user_id: str
) -> tuple[int, list[dict]]:
    logger.debug(f"Downloading anime with id: {anime_id}")
    success_enqueued = []
    failed_enqueued = []
    async with AsyncDatabaseSession() as db:
        for ep_number in episode_numbers:
            try:
                stmt = select(Episode).where(
                    Episode.anime_id == anime_id,
                    Episode.ep_number == ep_number,
                )
                episode = await db.scalar(stmt)
                if not episode:
                    raise NotFoundException("Episode not found")

                stmt = select(UserDownloadEpisode).where(
                    UserDownloadEpisode.episode_id == episode.id,
                    UserDownloadEpisode.user_id == user_id,
                )
                episode_download = await db.scalar(stmt)
                if episode_download:
                    logger.warning(
                        f"Episode {episode.id} already enqueued for "
                        + f"user {user_id}"
                    )
                    failed_enqueued.append([None, ep_number])
                    continue

                new_download = UserDownloadEpisode(
                    episode_id=episode.id, user_id=user_id
                )
                db.add(new_download)

                episode.status = "PENDING"
                db.add(episode)

                result = download_anime_episode.send(
                    anime_id, episode.ep_number, user_id
                )
                logger.debug(f"Enqueued download with job id: {result.message_id}")

                episode.job_id = result.message_id
                db.add(episode)
                await db.commit()
                success_enqueued.append([result.message_id, ep_number])
            except Exception as e:
                logger.error(f"Error downloading episode: {e}")
                failed_enqueued.append([None, ep_number])

        parsed_data = []
        for success in success_enqueued:
            parsed_data.append(
                {
                    "job_id": success[0],
                    "episode_number": success[1],
                    "success": True,
                }
            )
        for failed in failed_enqueued:
            parsed_data.append(
                {
                    "job_id": failed[0],
                    "episode_number": failed[1],
                    "success": False,
                }
            )
        casted_data = cast_download_task_list(parsed_data, len(parsed_data))
        return casted_data


async def get_animes_storage_controller(limit: int = 10, page: int = 1) -> dict:
    logger.info("Getting animes storage controller")
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Anime.id, Anime.title, func.sum(Episode.size).label("size"))
            .join(Anime.episodes)
            .where(
                Episode.size.isnot(None),
            )
            .group_by(Anime.id)
            .order_by(desc(func.sum(Episode.size)))
        )

        result = await db.execute(stmt)
        count = len(result.scalars().all())

        logger.debug(f"Found {count} animes")

        stmt = stmt.offset((page - 1) * limit).limit(limit)
        result = await db.execute(stmt)
        animes = result.all()

        animes_info = [
            {
                "id": anime.id,
                "title": anime.title,
                "size": anime.size,
            }
            for anime in animes
        ]

        casted_animes = cast_animes_storage_list(animes_info, count)

        return casted_animes


async def delete_anime_storage_controller(anime_id: str, user_id: str) -> str:
    logger.debug(f"Deleting anime with id: {anime_id}")
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Anime)
            .where(Anime.id == anime_id)
            .options(
                selectinload(Anime.episodes),
            )
        )
        result = await db.execute(stmt)
        anime = result.scalar()
        if not anime:
            raise NotFoundException("Anime not found")

        episode_ids = [ep.id for ep in anime.episodes]

        stmt = delete(UserDownloadEpisode).where(
            UserDownloadEpisode.episode_id.in_(episode_ids),
        )
        result = await db.execute(stmt)

        stmt = (
            update(Episode)
            .where(Episode.anime_id == anime_id)
            .values(
                size=None,
                job_id=None,
                status=None,
            )
        )

        await db.execute(stmt)

        logger.debug("Reset episode sizes and job ids")

        franchise_id = anime.franchise_id
        parsed_season = str(anime.season).zfill(2)

        if franchise_id:
            anime_folder = ANIMES_FOLDER / franchise_id / f"Season {parsed_season}"
        else:
            anime_folder = ANIMES_FOLDER / anime_id

        for episode in anime.episodes:
            parsed_ep_number = str(episode.ep_number).zfill(2)
            file_path = (
                anime_folder / f"{anime.id} - S{parsed_season}E{parsed_ep_number}.mp4"
            )

            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted file: {file_path}")
                logger.debug(f"Deleted episode: {episode.id}")

        if anime_folder.exists() and is_folder_empty(anime_folder):
            if franchise_id:
                shutil.rmtree(anime_folder)
                logger.debug(f"Deleted season folder: {anime_folder}")
            else:
                shutil.rmtree(anime_folder)
                logger.debug(f"Deleted anime folder: {anime_folder}")

        return "Anime storage deleted successfully"
