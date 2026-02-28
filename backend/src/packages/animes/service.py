import asyncio
from datetime import datetime, timezone
from pathlib import Path
from loguru import logger
from sqlalchemy import delete, desc, func, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert
from urllib.parse import unquote

from worker import download_anime_episode
from utils.exceptions import NotFoundException, ConflictException
from databases.postgres import (
    AsyncDatabaseSession,
    Anime,
    Genre,
    AnimeRelation,
    Episode,
    OtherTitle,
    UserSaveAnime,
    UserDownloadEpisode,
    related_types_id,
)
from .utils import (
    cast_animes_storage_list,
    cast_download_task_list,
    cast_downloaded_anime_list,
    cast_episode_download_list,
    cast_in_emission_anime_list,
    cast_job_id,
    cast_search_anime_result_list,
    cast_anime_info,
)
from .config import anime_settings
from .scraper import (
    scrape_anime_info,
    scrape_new_episodes,
    scrape_search_anime,
)

ANIMES_FOLDER = Path(anime_settings.ANIMES_FOLDER)


def get_anime_info_to_dict(
    anime_db: Anime,
    downloaded_user_episodes_ids: list[int],
    downloaded_global_episodes_ids: list[int],
) -> dict:
    return {
        "id": anime_db.id,
        "title": anime_db.title,
        "type": anime_db.type,
        "poster": anime_db.poster,
        "season": anime_db.season,
        "other_titles": [title.name for title in anime_db.other_titles],
        "description": anime_db.description,
        "genres": [genre.name for genre in anime_db.genres],
        "related_info": [
            {
                "id": related.related_anime.id,
                "title": related.related_anime.title,
                "type": related.type_related.name,
            }
            for related in anime_db.relations
        ],
        "week_day": anime_db.week_day,
        "is_finished": anime_db.is_finished,
        "last_scraped_at": anime_db.last_scraped_at,
        "last_forced_update": anime_db.last_forced_update,
        "episodes": [
            {
                "id": episode.ep_number,
                "anime_id": episode.anime_id,
                "image_preview": episode.preview,
                "is_user_downloaded": episode.id
                in downloaded_user_episodes_ids,
                "is_global_downloaded": episode.id
                in downloaded_global_episodes_ids,
            }
            for episode in anime_db.episodes
        ],
    }


async def get_user_anime_data(
    db: AsyncDatabaseSession, user_id: str, anime_id: str
) -> dict:
    """Obtiene datos de usuario para un anime específico."""
    stmt = select(UserSaveAnime).where(
        UserSaveAnime.user_id == user_id,
        UserSaveAnime.anime_id == anime_id,
    )
    result = await db.execute(stmt)
    saved_anime = result.scalar()

    stmt = select(Episode).where(Episode.anime_id == anime_id)
    result = await db.execute(stmt)
    episodes = result.scalars().all()
    episode_ids = [ep.id for ep in episodes]

    stmt = select(UserDownloadEpisode).where(
        UserDownloadEpisode.user_id == user_id,
        UserDownloadEpisode.episode_id.in_(episode_ids),
    )
    result = await db.execute(stmt)
    downloaded_user_episodes = result.scalars().all()

    stmt = select(UserDownloadEpisode).where(
        UserDownloadEpisode.episode_id.in_(episode_ids)
    )
    result = await db.execute(stmt)
    downloaded_global_episodes = result.scalars().all()

    saved_anime_info = {
        "is_saved": saved_anime is not None,
        "save_date": saved_anime.created_at if saved_anime else None,
    }

    downloaded_user_episodes_ids = [
        ep.episode_id for ep in downloaded_user_episodes
    ]
    downloaded_global_episodes_ids = [
        ep.episode_id for ep in downloaded_global_episodes
    ]

    return {
        "saved_anime_info": saved_anime_info,
        "downloaded_user_episodes_ids": downloaded_user_episodes_ids,
        "downloaded_global_episodes_ids": downloaded_global_episodes_ids,
    }


def build_anime_response(
    anime_db: Anime,
    downloaded_user_episodes_ids: list[int],
    downloaded_global_episodes_ids: list[int],
    saved_anime_info: dict,
) -> dict:
    """Construye la respuesta AnimeOut a partir del modelo DB y datos de usuario."""
    new_anime_info = get_anime_info_to_dict(
        anime_db,
        downloaded_user_episodes_ids,
        downloaded_global_episodes_ids,
    )
    return cast_anime_info(new_anime_info, saved_anime_info)


async def add_new_anime(
    db: AsyncDatabaseSession, base_url: str, anime_id: str
):
    logger.debug(f"Adding anime to database: {anime_id}")
    anime_info = await scrape_anime_info(anime_id, include_episodes=True)
    week_day = (
        anime_info.next_episode_date.strftime("%A")
        if anime_info.next_episode_date
        else None
    )
    current_time = datetime.now(timezone.utc)

    stmt = (
        insert(Anime)
        .values(
            id=anime_info.id,
            title=anime_info.title,
            description=anime_info.synopsis,
            poster=anime_info.poster,
            type=anime_info.type.value,
            is_finished=anime_info.is_finished,
            week_day=week_day,
            last_scraped_at=current_time,
            last_forced_update=current_time,
        )
        .on_conflict_do_update(
            index_elements=["id"],
            set_={
                "title": anime_info.title,
                "description": anime_info.synopsis,
                "poster": anime_info.poster,
                "type": anime_info.type.value,
                "is_finished": anime_info.is_finished,
                "week_day": week_day,
                "last_scraped_at": current_time,
                "last_forced_update": current_time,
            },
        )
    )
    await db.execute(stmt)
    logger.debug(f"Upserted anime: {anime_info.id}")

    genre_values = [
        {"anime_id": anime_info.id, "name": g} for g in anime_info.genres
    ]
    if genre_values:
        stmt = insert(Genre).values(genre_values).on_conflict_do_nothing()
        await db.execute(stmt)
    logger.debug("Inserted genres")

    for related in anime_info.related_info:
        stmt_anime = (
            insert(Anime)
            .values(id=related.id, title=related.title)
            .on_conflict_do_nothing(index_elements=["id"])
        )
        await db.execute(stmt_anime)

        stmt_relation = (
            insert(AnimeRelation)
            .values(
                anime_id=anime_info.id,
                related_anime_id=related.id,
                type_related_id=related_types_id[related.type.value],
            )
            .on_conflict_do_nothing()
        )
        await db.execute(stmt_relation)
    logger.debug("Inserted related animes")

    other_titles_values = [
        {"anime_id": anime_info.id, "name": t} for t in anime_info.other_titles
    ]
    if other_titles_values:
        stmt = (
            insert(OtherTitle)
            .values(other_titles_values)
            .on_conflict_do_nothing(index_elements=["anime_id", "name"])
        )
        await db.execute(stmt)
    logger.debug("Inserted other titles")

    episode_values = [
        {
            "anime_id": anime_info.id,
            "ep_number": ep.number,
            "preview": ep.image_preview,
            "url": f"{base_url}/{ep.number}",
        }
        for ep in anime_info.episodes
    ]
    if episode_values:
        stmt = (
            insert(Episode)
            .values(episode_values)
            .on_conflict_do_nothing(index_elements=["anime_id", "ep_number"])
        )
        await db.execute(stmt)
    logger.debug("Inserted episodes")

    await db.flush()


async def update_anime_info(
    db: AsyncDatabaseSession, anime_db: Anime, base_url: str, anime_id: str
) -> Anime:
    """Actualiza la información de un anime existente."""
    current_time = datetime.now(timezone.utc)

    anime_info = await scrape_anime_info(anime_id, include_episodes=False)

    anime_db.title = anime_info.title
    anime_db.description = anime_info.synopsis
    anime_db.poster = anime_info.poster
    anime_db.type = anime_info.type.value
    anime_db.is_finished = anime_info.is_finished
    anime_db.week_day = (
        anime_info.next_episode_date.strftime("%A")
        if anime_info.next_episode_date
        else None
    )
    anime_db.last_scraped_at = current_time
    anime_db.last_forced_update = current_time
    db.add(anime_db)

    await asyncio.sleep(1.5)
    last_ep_number = max([ep.ep_number for ep in anime_db.episodes], default=0)
    new_episodes = await scrape_new_episodes(anime_id, last_ep_number)

    for ep in new_episodes:
        new_episode = Episode(
            anime_id=anime_id,
            ep_number=ep.number,
            preview=ep.image_preview,
            url=f"{base_url}/{ep.number}",
        )
        db.add(new_episode)

    await db.flush()
    return anime_db


async def update_anime_controller(anime_id: str, user_id: str) -> dict:
    """Actualiza un anime bajo demanda con validación de cooldown."""
    base_url = f"https://jkanime.net/{anime_id}"

    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Anime)
            .where(Anime.id == anime_id)
            .options(
                selectinload(Anime.other_titles),
                selectinload(Anime.genres),
                selectinload(Anime.episodes),
                selectinload(Anime.relations),
            )
        )
        result = await db.execute(stmt)
        anime_db = result.scalar()

        anime_db = await update_anime_info(db, anime_db, base_url, anime_id)
        await db.commit()

        await db.refresh(anime_db, attribute_names=["episodes"])

        user_data = await get_user_anime_data(db, user_id, anime_id)

        response = build_anime_response(
            anime_db,
            user_data["downloaded_user_episodes_ids"],
            user_data["downloaded_global_episodes_ids"],
            user_data["saved_anime_info"],
        )

    return response


async def get_anime_controller(anime_id: str, user_id: str) -> dict:
    """Obtiene información de un anime. Crea si no existe, devuelve sin actualizar."""
    logger.debug(f"Getting anime with id: {anime_id}")
    base_url = f"https://jkanime.net/{anime_id}"

    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Anime)
            .where(Anime.id == anime_id)
            .options(
                selectinload(Anime.other_titles),
                selectinload(Anime.genres),
                selectinload(Anime.episodes),
                selectinload(Anime.relations),
            )
        )
        result = await db.execute(stmt)
        anime_db = result.scalar()

        if not anime_db or not anime_db.last_scraped_at:
            logger.debug("Anime not in DB or dummy row found, creating...")
            await add_new_anime(db, base_url, anime_id)
            stmt = (
                select(Anime)
                .where(Anime.id == anime_id)
                .options(
                    selectinload(Anime.other_titles),
                    selectinload(Anime.genres),
                    selectinload(Anime.episodes),
                    selectinload(Anime.relations),
                )
            )
            result = await db.execute(stmt)
            anime_db = result.scalar()

        user_data = await get_user_anime_data(db, user_id, anime_id)

        response = build_anime_response(
            anime_db,
            user_data["downloaded_user_episodes_ids"],
            user_data["downloaded_global_episodes_ids"],
            user_data["saved_anime_info"],
        )

        return response


async def search_anime_controller(query: str, user_id: str):
    logger.debug(f"Searching for {query}")
    query = unquote(query)
    animes = await scrape_search_anime(query)
    logger.debug(f"Found {len(animes.animes)} animes")

    async with AsyncDatabaseSession() as db:
        stmt = (
            select(UserSaveAnime)
            .where(UserSaveAnime.user_id == user_id)
            .options(selectinload(UserSaveAnime.anime))
        )
        result = await db.execute(stmt)
        saved_animes = result.scalars().all()

        saved_ids = [anime.anime_id for anime in saved_animes]

        search_animes = [
            {
                "id": anime.id,
                "title": anime.title,
                "type": anime.type.value,
                "poster": anime.poster,
                "is_saved": anime.id in saved_ids,
                "save_date": (
                    saved_animes[saved_ids.index(anime.id)].created_at
                    if anime.id in saved_ids
                    else None
                ),
            }
            for anime in animes.animes
        ]

        casted_animes = cast_search_anime_result_list(search_animes)
        return casted_animes


async def get_saved_animes_controller(user_id: str) -> dict:
    logger.debug("Getting saved animes")
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(UserSaveAnime)
            .where(UserSaveAnime.user_id == user_id)
            .options(selectinload(UserSaveAnime.anime))
        )
        result = await db.execute(stmt)
        animes_db = result.scalars().all()

        animes = [
            {
                "id": anime.anime.id,
                "title": anime.anime.title,
                "type": anime.anime.type,
                "poster": anime.anime.poster,
                "is_saved": True,
                "save_date": anime.anime.created_at,
            }
            for anime in animes_db
        ]

        casted_animes = cast_search_anime_result_list(animes)
        return casted_animes


async def save_anime_controller(anime_id: str, user_id: str) -> str:
    logger.debug(f"Saving anime with id: {anime_id}")
    base_url = f"https://jkanime.net/{anime_id}"
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Anime)
            .where(Anime.id == anime_id)
            .options(
                selectinload(Anime.other_titles),
                selectinload(Anime.genres),
                selectinload(Anime.episodes),
                selectinload(Anime.relations),
            )
        )
        result = await db.execute(stmt)
        anime_db = result.scalar()
        if not anime_db or not anime_db.last_scraped_at:
            await add_new_anime(db, base_url, anime_id)
        new_saved_anime = UserSaveAnime(
            user_id=user_id,
            anime_id=anime_id,
        )
        db.add(new_saved_anime)
        await db.flush()
        logger.debug(f"Saved anime with id: {anime_id}")

        return "Anime saved successfully"


async def unsave_anime_controller(anime_id: str, user_id: str) -> str:
    logger.debug(f"Unsaving anime with id: {anime_id}")
    async with AsyncDatabaseSession() as db:
        stmt = select(UserSaveAnime).where(
            UserSaveAnime.user_id == user_id,
            UserSaveAnime.anime_id == anime_id,
        )
        result = await db.execute(stmt)
        saved_anime = result.scalar()
        await db.delete(saved_anime)
        logger.debug(f"Unsaved anime with id: {anime_id}")

        return "Anime unsaved successfully"


async def get_in_emission_animes_controller(user_id: str) -> dict:
    logger.debug("Getting in-emission animes")
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(UserSaveAnime)
            .join(UserSaveAnime.anime)
            .options(selectinload(UserSaveAnime.anime))
            .where(
                UserSaveAnime.user_id == user_id,
                Anime.week_day.isnot(None),
                Anime.is_finished.is_(False),
            )
        )
        result = await db.execute(stmt)
        animes_db = result.scalars().all()
        animes = [
            {
                "id": anime.anime.id,
                "title": anime.anime.title,
                "type": anime.anime.type,
                "poster": anime.anime.poster,
                "is_saved": True,
                "save_date": anime.anime.created_at,
                "week_day": anime.anime.week_day,
            }
            for anime in animes_db
            if anime.anime.week_day
        ]

        casted_animes = cast_in_emission_anime_list(animes)
        return casted_animes


async def get_download_episodes_controller(
    user_id: str, anime_id: str | None = None, limit: int = 10, page: int = 1
) -> tuple[int, dict]:
    logger.debug("Getting downloads")

    async with AsyncDatabaseSession() as db:
        stmt = (
            select(UserDownloadEpisode)
            .where(UserDownloadEpisode.user_id == user_id)
            .options(
                selectinload(UserDownloadEpisode.episode).selectinload(
                    Episode.anime
                ),
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

        casted_episode_downloads = cast_episode_download_list(
            episode_downloads, count
        )

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
                selectinload(UserDownloadEpisode.episode).selectinload(
                    Episode.anime
                ),
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
            episode_download.episode.anime_id
            for episode_download in episode_downloads
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


async def delete_download_episode_controller(
    episode_id: int, user_id: str
) -> str:
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
            anime_folder = (
                ANIMES_FOLDER / episode.anime_id / f"Season {parsed_season}"
            )
            if franchise_id:
                anime_folder = (
                    ANIMES_FOLDER / franchise_id / f"Season {parsed_season}"
                )
            if not anime_folder.exists():
                raise NotFoundException("Episode file not found")

            ep_number = str(episode.ep_number).zfill(2)
            file_path = (
                anime_folder
                / f"{episode.anime_id} - S{parsed_season}E{ep_number}.mp4"
            )
            if file_path.exists():
                file_path.unlink()

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


async def get_animes_storage_controller(
    limit: int = 10, page: int = 1
) -> dict:
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

        for episode in anime.episodes:
            parsed_season = str(episode.anime.season).zfill(2)
            parsed_ep_number = str(episode.ep_number).zfill(2)
            file_path = (
                ANIMES_FOLDER
                / anime_id
                / f"Season {parsed_season}"
                / f"{anime.id} - S{parsed_season}E{parsed_ep_number}.mp4"
            )

            print("file path", str(file_path))

            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted file: {file_path}")
                logger.debug(f"Deleted episode: {episode.id}")

        return "Anime storage deleted successfully"
