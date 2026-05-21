from fastapi import Depends

from packages.auth import auth_scheme
from exceptions import NotFoundError

from . import repository


async def valid_franchise_id(
    franchise_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Validates that the franchise exists and returns the required data."""
    franchise = await repository.get_franchise_by_id(franchise_id)
    if not franchise:
        raise NotFoundError(f"Franchise {franchise_id} not found")

    return {
        "franchise_id": franchise_id,
        "franchise": franchise,
        "user_id": current_user["id"],
    }


async def valid_anime_for_franchise(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Validates that the anime exists and has no franchise assigned yet."""
    anime = await repository.get_anime_without_franchise(anime_id)
    if not anime:
        raise NotFoundError(
            f"Anime {anime_id} not found or already has franchise"
        )

    return {
        "anime_id": anime_id,
        "anime": anime,
        "user_id": current_user["id"],
    }
