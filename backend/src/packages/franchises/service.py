from loguru import logger
from sqlalchemy import asc, insert, select
from sqlalchemy.orm import selectinload

from worker import order_franchise
from databases.postgres import AsyncDatabaseSession, Anime, Franchise
from utils.utils import to_kebab_case
from utils.exceptions import ConflictException
from .schemas import CreateFranchise
from .utils import cast_anime_franchise_list, cast_franchise_list


async def get_franchises_controller(user_id: str) -> dict:
    logger.debug("Getting franchises")
    async with AsyncDatabaseSession() as db:
        stmt = select(Franchise).options(
            selectinload(Franchise.animes),
        )
        result = await db.execute(stmt)
        franchises = result.scalars().all()

        franchises_info = [
            {
                "id": franchise.id,
                "name": franchise.name,
                "animes": [
                    {
                        "id": anime.id,
                        "title": anime.title,
                        "type": anime.type,
                        "poster": anime.poster,
                        "is_saved": anime.id in user_id,
                        "save_date": anime.created_at,
                    }
                    for anime in franchise.animes
                ],
            }
            for franchise in franchises
        ]
        total = len(franchises)

        casted_franchises = cast_franchise_list(franchises_info, total)
        return casted_franchises


async def create_franchise_controller(franchise_info: CreateFranchise) -> str:
    logger.debug("Creating franchise")
    async with AsyncDatabaseSession() as db:
        animes_ids = [anime.id for anime in franchise_info.animes]
        logger.debug(f"Animes ids: {animes_ids}")

        stmt = select(Anime).where(Anime.id.in_(animes_ids))
        result = await db.execute(stmt)
        animes = result.scalars().all()

        logger.debug(f"Inserting franchise: {franchise_info.franchise}")
        franchise_id = to_kebab_case(franchise_info.franchise)

        animes_ids = [anime.id for anime in franchise_info.animes]
        if franchise_id in animes_ids:
            logger.debug(f"Franchise name share by anime: {franchise_id}")
            raise ConflictException("Franchise name share by anime")

        stmt = insert(Franchise).values(
            id=franchise_id, name=franchise_info.franchise
        )
        await db.execute(stmt)

        logger.debug(f"Inserted franchise: {franchise_id}")

        for anime in animes:
            logger.debug(f"Updating anime: {anime.id}")
            anime.franchise_id = franchise_id
            db.add(anime)

        franchise_info = {
            "id": franchise_id,
            "name": franchise_info.franchise,
            "animes": [
                {
                    "id": anime.id,
                    "season": anime.season,
                }
                for anime in franchise_info.animes
            ],
        }

        order_franchise.send(franchise_info)

        return "Franchise created successfully"


async def get_animes_for_franchises_controller(
    user_id: str,
) -> dict:
    logger.debug("Getting animes")
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(Anime)
            .where(Anime.poster.isnot(None))
            .where(Anime.franchise_id.is_(None))
            .options(
                selectinload(Anime.franchise),
            )
            .order_by(asc(Anime.title))
        )
        result = await db.execute(stmt)
        animes = result.scalars().all()

        animes_info = [
            {
                "id": anime.id,
                "title": anime.title,
                "type": anime.type,
                "poster": anime.poster,
                "is_saved": anime.id in user_id,
                "save_date": anime.created_at,
                "franchise": anime.franchise.name if anime.franchise else None,
            }
            for anime in animes
        ]

        casted_animes = cast_anime_franchise_list(animes_info)
        return casted_animes
