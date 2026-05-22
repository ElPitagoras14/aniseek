import asyncio
from datetime import datetime, timezone
from urllib.parse import unquote

from loguru import logger

from database.client import db
from database.utils import related_types_id

from . import repository
from .scraper import scrape_anime_info, scrape_new_episodes, scrape_search_anime
from .utils import (
    cast_anime_info,
    cast_in_emission_anime_list,
    cast_saved_anime_result_list,
    cast_search_anime_result_list,
)


def get_anime_info_to_dict(anime_db: dict) -> dict:
    return {
        "id": anime_db["id"],
        "title": anime_db["title"],
        "type": anime_db["type"],
        "poster": anime_db["poster"],
        "season": anime_db["season"],
        "description": anime_db["description"],
        "genres": anime_db["genres"],
        "related_info": [
            {
                "id": rel["related_anime_id"],
                "title": rel["related_title"],
                "type": rel["type_related_name"],
            }
            for rel in anime_db["relations"]
        ],
        "week_day": anime_db["week_day"],
        "is_finished": anime_db["is_finished"],
        "last_scraped_at": anime_db["last_scraped_at"],
        "episodes": [
            {
                "id": ep["ep_number"],
                "anime_id": ep["anime_id"],
                "image_preview": ep["preview"],
                "is_user_downloaded": ep["is_user_downloaded"],
                "is_global_downloaded": ep["is_global_downloaded"],
            }
            for ep in anime_db["episodes"]
        ],
    }


def build_anime_response(anime_db: dict) -> dict:
    return cast_anime_info(get_anime_info_to_dict(anime_db), anime_db["saved_info"])


async def add_new_anime(base_url: str, anime_id: str) -> None:
    logger.debug(f"Adding anime to database: {anime_id}")
    anime_info = await scrape_anime_info(anime_id, include_episodes=True)
    week_day = (
        anime_info.next_episode_date.strftime("%A")
        if anime_info.next_episode_date
        else None
    )
    current_time = datetime.now(timezone.utc)

    async with db.transaction():
        await repository.upsert_scraped_anime(
            {
                "id": anime_info.id,
                "title": anime_info.title,
                "description": anime_info.description,
                "poster": anime_info.poster,
                "type": anime_info.type.value,
                "is_finished": anime_info.is_finished,
                "week_day": week_day,
                "last_scraped_at": current_time,
            }
        )
        logger.debug(f"Upserted anime: {anime_info.id}")

        await repository.insert_genres(anime_info.id, list(anime_info.genres))
        logger.debug("Inserted genres")

        for related in anime_info.related_info:
            await repository.insert_dummy_anime(related.id, related.title)
            await repository.insert_anime_relation(
                anime_info.id, related.id, related_types_id[related.type.value]
            )
        logger.debug("Inserted related animes")

        episode_values = [
            {
                "anime_id": anime_info.id,
                "ep_number": ep.episode_number,
                "preview": ep.image_preview,
                "url": f"{base_url}/{ep.episode_number}",
            }
            for ep in anime_info.episodes
        ]
        await repository.insert_episodes(episode_values)
        logger.debug("Inserted episodes")


async def update_anime_info(base_url: str, anime_id: str) -> None:
    current_time = datetime.now(timezone.utc)
    anime_info = await scrape_anime_info(anime_id, include_episodes=False)

    week_day = (
        anime_info.next_episode_date.strftime("%A")
        if anime_info.next_episode_date
        else None
    )

    async with db.transaction():
        await repository.update_anime_fields(
            anime_id,
            {
                "title": anime_info.title,
                "description": anime_info.description,
                "poster": anime_info.poster,
                "type": anime_info.type.value,
                "is_finished": anime_info.is_finished,
                "week_day": week_day,
                "last_scraped_at": current_time,
            },
        )

        for related in anime_info.related_info:
            await repository.insert_dummy_anime(related.id, related.title)
            await repository.insert_anime_relation(
                anime_info.id, related.id, related_types_id[related.type.value]
            )

        await asyncio.sleep(1.5)
        last_ep_number = await repository.get_max_episode_number(anime_id)
        new_episodes = await scrape_new_episodes(anime_id, last_ep_number)

        await repository.insert_new_episodes(
            anime_id,
            [
                {
                    "anime_id": anime_id,
                    "ep_number": ep.episode_number,
                    "preview": ep.image_preview,
                    "url": f"{base_url}/{ep.episode_number}",
                }
                for ep in new_episodes
            ],
        )


async def update_anime_controller(anime_id: str, user_id: str) -> dict:
    base_url = f"https://animeav1.com/media/{anime_id}"
    await update_anime_info(base_url, anime_id)
    anime_db = await repository.get_anime_with_relations(anime_id, user_id)
    return build_anime_response(anime_db)


async def get_anime_controller(anime_id: str, user_id: str) -> dict:
    logger.debug(f"Getting anime with id: {anime_id}")
    base_url = f"https://animeav1.com/media/{anime_id}"

    anime_db = await repository.get_anime_with_relations(anime_id, user_id)

    if not anime_db or not anime_db.get("last_scraped_at"):
        logger.debug("Anime not in DB or dummy row found, creating...")
        await add_new_anime(base_url, anime_id)
        anime_db = await repository.get_anime_with_relations(anime_id, user_id)

    return build_anime_response(anime_db)


async def search_anime_controller(query: str, user_id: str):
    logger.debug(f"Searching for {query}")
    query = unquote(query)
    animes = await scrape_search_anime(query)
    logger.debug(f"Found {len(animes.animes)} animes")

    saved = await repository.list_user_saved_animes(user_id)
    saved_by_id = {a["id"]: a for a in saved}

    search_animes = [
        {
            "id": anime.id,
            "title": anime.title,
            "type": anime.type,
            "poster": anime.poster,
            "is_saved": anime.id in saved_by_id,
            "save_date": (
                saved_by_id[anime.id]["save_date"] if anime.id in saved_by_id else None
            ),
        }
        for anime in animes.animes
    ]
    return cast_search_anime_result_list(search_animes)


async def get_saved_animes_controller(user_id: str) -> dict:
    logger.debug("Getting saved animes")
    saved = await repository.list_user_saved_animes(user_id)

    animes = [
        {
            "id": a["id"],
            "title": a["title"],
            "type": a["type"],
            "poster": a["poster"],
            "is_saved": True,
            "save_date": a["save_date"],
            "is_finished": a["is_finished"],
        }
        for a in saved
    ]
    return cast_saved_anime_result_list(animes)


async def save_anime_controller(anime_id: str, user_id: str) -> str:
    logger.debug(f"Saving anime with id: {anime_id}")
    base_url = f"https://animeav1.com/media/{anime_id}"

    anime_db = await repository.get_anime_by_id(anime_id)
    if not anime_db or not anime_db.get("last_scraped_at"):
        await add_new_anime(base_url, anime_id)

    await repository.insert_user_saved_anime(user_id, anime_id)
    logger.debug(f"Saved anime with id: {anime_id}")
    return "Anime saved successfully"


async def unsave_anime_controller(anime_id: str, user_id: str) -> str:
    logger.debug(f"Unsaving anime with id: {anime_id}")
    await repository.delete_user_saved_anime(user_id, anime_id)
    logger.debug(f"Unsaved anime with id: {anime_id}")
    return "Anime unsaved successfully"


async def get_in_emission_animes_controller(user_id: str) -> dict:
    logger.debug("Getting in-emission animes")
    rows = await repository.list_user_saved_in_emission_animes(user_id)

    animes = [
        {
            "id": r["id"],
            "title": r["title"],
            "type": r["type"],
            "poster": r["poster"],
            "is_saved": True,
            "save_date": r["created_at"],
            "week_day": r["week_day"],
        }
        for r in rows
        if r["week_day"]
    ]
    return cast_in_emission_anime_list(animes)
