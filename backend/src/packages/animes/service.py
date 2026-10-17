import asyncio
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote

from loguru import logger

from database.client import engine
from database.utils import related_types_id
from exceptions import ConflictError, NotFoundError, TooManyRequestsError

from . import repository
from .catalog import episode_url
from .scraper import scrape_anime_info, scrape_search_anime
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
                "url": ep["url"],
                "is_user_downloaded": ep["is_user_downloaded"],
                "is_global_downloaded": ep["is_global_downloaded"],
            }
            for ep in anime_db["episodes"]
        ],
    }


def build_anime_response(anime_db: dict) -> dict:
    return cast_anime_info(get_anime_info_to_dict(anime_db), anime_db["saved_info"])


def _anime_fields_from_info(anime_info, current_time: datetime) -> dict:
    week_day = (
        anime_info.next_episode_date.strftime("%A")
        if anime_info.next_episode_date
        else None
    )
    return {
        "title": anime_info.title,
        "description": anime_info.description,
        "poster": anime_info.poster,
        "type": anime_info.type.value,
        "is_finished": anime_info.is_finished,
        "week_day": week_day,
        "last_scraped_at": current_time,
    }


def _episode_values(episodes, anime_id: str) -> list[dict]:
    return [
        {
            "anime_id": anime_id,
            "ep_number": ep.episode_number,
            "preview": ep.image_preview,
            "url": episode_url(anime_id, ep.episode_number),
        }
        for ep in episodes
    ]


def _relation_rows(anime_info) -> tuple[list[dict], list[dict]]:
    """Builds the placeholder-anime rows and the relation rows for a scraped
    anime. Relations whose type is unknown are logged and skipped."""
    placeholders: list[dict] = []
    relations: list[dict] = []
    for related in anime_info.related_info:
        type_id = related_types_id.get(related.type.value)
        if type_id is None:
            logger.warning(
                f"Skipping relation {anime_info.id} -> {related.id}: "
                f"unknown relation type {related.type.value!r}"
            )
            continue
        placeholders.append({"id": related.id, "title": related.title})
        relations.append(
            {
                "anime_id": anime_info.id,
                "related_anime_id": related.id,
                "type_related_id": type_id,
            }
        )
    return placeholders, relations


def is_scraped(row: dict | None) -> bool:
    """An anime counts as scraped only if a sync has completed for it; a
    placeholder row (created as someone's relation) is treated as missing."""
    return bool(row and row.get("last_scraped_at"))


async def _scrape_snapshot(anime_id: str):
    # Single GET to the provider, with no DB connection held.
    return await scrape_anime_info(anime_id, include_episodes=True)


async def _persist_snapshot(conn, anime_info, current_time: datetime) -> None:
    anime_fields = _anime_fields_from_info(anime_info, current_time)
    await repository.upsert_scraped_anime(conn, {"id": anime_info.id, **anime_fields})
    await repository.insert_genres(conn, anime_info.id, list(anime_info.genres))
    placeholders, relations = _relation_rows(anime_info)
    await repository.upsert_relations(conn, placeholders, relations)
    await repository.insert_episodes(
        conn, _episode_values(anime_info.episodes, anime_info.id)
    )


async def _do_sync(anime_id: str) -> None:
    logger.debug(f"Syncing anime: {anime_id}")
    # All external I/O happens before the write transaction opens, so no pool
    # connection is held while waiting on the network.
    current_time = datetime.now(timezone.utc)
    anime_info = await _scrape_snapshot(anime_id)

    async with engine.begin() as conn:
        await _persist_snapshot(conn, anime_info, current_time)


# Single-flight de syncs por anime. Supone UN solo proceso del backend
# (uvicorn sin workers, un unico contenedor): con varios procesos o replicas
# esto deja de deduplicar y habria que migrar a un lock en Redis.
_sync_inflight: dict[str, asyncio.Task] = {}


async def sync_anime(anime_id: str) -> None:
    task = _sync_inflight.get(anime_id)
    if task is None:
        task = asyncio.create_task(_do_sync(anime_id))
        _sync_inflight[anime_id] = task
        # Drop the entry whether it succeeded or failed, so errors aren't memoized.
        task.add_done_callback(lambda _: _sync_inflight.pop(anime_id, None))
    # shield: if a waiter is cancelled (client disconnect), the shared sync
    # that other waiters depend on keeps running.
    await asyncio.shield(task)


async def ensure_anime_scraped(anime_id: str) -> None:
    async with engine.connect() as conn:
        anime_db = await repository.get_anime_by_id(conn, anime_id)
    if not is_scraped(anime_db):
        logger.debug(f"Anime {anime_id} not scraped yet, syncing...")
        await sync_anime(anime_id)


REFRESH_COOLDOWN = timedelta(minutes=5)


async def assert_anime_exists(anime_id: str) -> None:
    """404 unless the anime has a row (placeholder or scraped)."""
    async with engine.connect() as conn:
        anime = await repository.get_anime_by_id(conn, anime_id)
    if not anime:
        raise NotFoundError(f"Anime {anime_id} not found")


async def assert_anime_refreshable(anime_id: str) -> None:
    """The anime must be scraped and its last sync older than the cooldown."""
    async with engine.connect() as conn:
        anime = await repository.get_anime_by_id(conn, anime_id)

    if not is_scraped(anime):
        raise NotFoundError(
            "Anime not found or not yet created. "
            "Use GET /animes/{anime_id} to create it first."
        )

    last_scraped = anime["last_scraped_at"]
    if last_scraped.tzinfo is None:
        last_scraped = last_scraped.replace(tzinfo=timezone.utc)

    elapsed = datetime.now(timezone.utc) - last_scraped
    if elapsed < REFRESH_COOLDOWN:
        remaining_seconds = int((REFRESH_COOLDOWN - elapsed).total_seconds())
        raise TooManyRequestsError(
            f"Anime was updated recently. "
            f"Please wait {remaining_seconds} seconds before updating."
        )


async def load_anime_detail(anime_id: str, user_id: str) -> dict:
    """The anime row with genres, relations, saved info and its episodes
    (number, status and the user's download flag), as the repository returns it."""
    async with engine.connect() as conn:
        return await repository.get_anime_with_relations(conn, anime_id, user_id)


async def refresh_anime(anime_id: str) -> None:
    await assert_anime_refreshable(anime_id)
    await sync_anime(anime_id)


async def update_anime_controller(anime_id: str, user_id: str) -> dict:
    await refresh_anime(anime_id)
    return build_anime_response(await load_anime_detail(anime_id, user_id))


async def get_anime_controller(anime_id: str, user_id: str) -> dict:
    logger.debug(f"Getting anime with id: {anime_id}")
    await ensure_anime_scraped(anime_id)
    return build_anime_response(await load_anime_detail(anime_id, user_id))


async def search_anime_controller(query: str, user_id: str):
    logger.debug(f"Searching for {query}")
    query = unquote(query)
    animes = await scrape_search_anime(query)
    logger.debug(f"Found {len(animes.animes)} animes")

    async with engine.connect() as conn:
        saved = await repository.list_user_saved_animes(conn, user_id)
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
    async with engine.connect() as conn:
        saved = await repository.list_user_saved_animes(conn, user_id)

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
    # Does not require the anime to exist yet: saving one creates it.
    async with engine.connect() as conn:
        saved = await repository.get_user_saved_anime(conn, user_id, anime_id)
    if saved:
        raise ConflictError("Anime already saved by user")

    await ensure_anime_scraped(anime_id)

    async with engine.begin() as conn:
        await repository.insert_user_saved_anime(conn, user_id, anime_id)
    logger.debug(f"Saved anime with id: {anime_id}")
    return "Anime saved successfully"


async def unsave_anime_controller(anime_id: str, user_id: str) -> str:
    logger.debug(f"Unsaving anime with id: {anime_id}")
    await assert_anime_exists(anime_id)
    async with engine.connect() as conn:
        saved = await repository.get_user_saved_anime(conn, user_id, anime_id)
    if not saved:
        raise NotFoundError("Anime not saved by user")

    async with engine.begin() as conn:
        await repository.delete_user_saved_anime(conn, user_id, anime_id)
    logger.debug(f"Unsaved anime with id: {anime_id}")
    return "Anime unsaved successfully"


async def get_in_emission_animes_controller(user_id: str) -> dict:
    logger.debug("Getting in-emission animes")
    async with engine.connect() as conn:
        rows = await repository.list_user_saved_in_emission_animes(conn, user_id)

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
