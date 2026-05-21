import asyncio
from datetime import datetime, timezone
from urllib.parse import unquote

from loguru import logger
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from databases.postgres import (
    Anime,
    AnimeRelation,
    AsyncDatabaseSession,
    Episode,
    Genre,
    UserDownloadEpisode,
    UserSaveAnime,
    related_types_id,
)

from .scraper import scrape_anime_info, scrape_new_episodes, scrape_search_anime
from .utils import (
    cast_anime_info,
    cast_in_emission_anime_list,
    cast_search_anime_result_list,
)

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
        "episodes": [
            {
                "id": episode.ep_number,
                "anime_id": episode.anime_id,
                "image_preview": episode.preview,
                "is_user_downloaded": episode.id in downloaded_user_episodes_ids,
                "is_global_downloaded": episode.id in downloaded_global_episodes_ids,
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

    downloaded_user_episodes_ids = [ep.episode_id for ep in downloaded_user_episodes]
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


async def add_new_anime(db: AsyncDatabaseSession, base_url: str, anime_id: str):
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
            description=anime_info.description,
            poster=anime_info.poster,
            type=anime_info.type.value,
            is_finished=anime_info.is_finished,
            week_day=week_day,
            last_scraped_at=current_time,
        )
        .on_conflict_do_update(
            index_elements=["id"],
            set_={
                "title": anime_info.title,
                "description": anime_info.description,
                "poster": anime_info.poster,
                "type": anime_info.type.value,
                "is_finished": anime_info.is_finished,
                "week_day": week_day,
                "last_scraped_at": current_time,
            },
        )
    )
    await db.execute(stmt)
    logger.debug(f"Upserted anime: {anime_info.id}")

    genre_values = [{"anime_id": anime_info.id, "name": g} for g in anime_info.genres]
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
    anime_db.description = anime_info.description
    anime_db.poster = anime_info.poster
    anime_db.type = anime_info.type.value
    anime_db.is_finished = anime_info.is_finished
    anime_db.week_day = (
        anime_info.next_episode_date.strftime("%A")
        if anime_info.next_episode_date
        else None
    )
    anime_db.last_scraped_at = current_time
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
    base_url = f"https://animeav1.com/media/{anime_id}"

    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Anime)
            .where(Anime.id == anime_id)
            .options(
                selectinload(Anime.genres),
                selectinload(Anime.episodes),
                selectinload(Anime.relations).selectinload(AnimeRelation.related_anime),
                selectinload(Anime.relations).selectinload(AnimeRelation.type_related),
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
    base_url = f"https://animeav1.com/media/{anime_id}"

    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Anime)
            .where(Anime.id == anime_id)
            .options(
                selectinload(Anime.genres),
                selectinload(Anime.episodes),
                selectinload(Anime.relations).selectinload(AnimeRelation.related_anime),
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
                    selectinload(Anime.genres),
                    selectinload(Anime.episodes),
                    selectinload(Anime.relations).selectinload(
                        AnimeRelation.related_anime
                    ),
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
                "type": anime.type,
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
    base_url = f"https://animeav1.com/media/{anime_id}"
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Anime)
            .where(Anime.id == anime_id)
            .options(
                selectinload(Anime.genres),
                selectinload(Anime.episodes),
                selectinload(Anime.relations).selectinload(AnimeRelation.related_anime),
                selectinload(Anime.relations).selectinload(AnimeRelation.type_related),
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

