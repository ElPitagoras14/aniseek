from loguru import logger

from database.client import db
from exceptions import ConflictError
from utils import to_kebab_case
from worker import order_franchise

from . import repository
from .schemas import FranchiseCreate
from .utils import cast_anime_franchise_list, cast_franchise_list


async def get_franchises_controller(user_id: str) -> dict:
    logger.debug("Getting franchises")
    rows = await repository.list_franchises_with_animes()

    grouped: dict[str, dict] = {}
    for row in rows:
        fid = row["franchise_id"]
        if fid not in grouped:
            grouped[fid] = {
                "id": fid,
                "name": row["franchise_name"],
                "animes": [],
            }
        if row["anime_id"] is not None:
            grouped[fid]["animes"].append(
                {
                    "id": row["anime_id"],
                    "title": row["title"],
                    "type": row["type"],
                    "poster": row["poster"],
                    "is_saved": row["anime_id"] in user_id,
                    "save_date": row["anime_created_at"],
                }
            )

    franchises_info = list(grouped.values())
    return cast_franchise_list(franchises_info, len(franchises_info))


async def create_franchise_controller(franchise_info: FranchiseCreate) -> str:
    logger.debug("Creating franchise")
    animes_ids = [anime.id for anime in franchise_info.animes]
    logger.debug(f"Animes ids: {animes_ids}")

    franchise_id = to_kebab_case(franchise_info.franchise)

    if franchise_id in animes_ids:
        logger.debug(f"Franchise name share by anime: {franchise_id}")
        raise ConflictError("Franchise name share by anime")

    async with db.transaction():
        await repository.insert_franchise(franchise_id, franchise_info.franchise)
        logger.debug(f"Inserted franchise: {franchise_id}")
        await repository.assign_animes_to_franchise(animes_ids, franchise_id)

    franchise_payload = {
        "id": franchise_id,
        "name": franchise_info.franchise,
        "animes": [
            {"id": anime.id, "season": anime.season} for anime in franchise_info.animes
        ],
    }
    order_franchise.send(franchise_payload)

    return "Franchise created successfully"


async def get_animes_for_franchises_controller(user_id: str) -> dict:
    logger.debug("Getting animes")
    animes = await repository.list_animes_without_franchise()

    animes_info = [
        {
            "id": anime["id"],
            "title": anime["title"],
            "type": anime["type"],
            "poster": anime["poster"],
            "is_saved": anime["id"] in user_id,
            "save_date": anime["created_at"],
            "franchise": None,
        }
        for anime in animes
    ]
    return cast_anime_franchise_list(animes_info)
