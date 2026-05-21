from datetime import datetime, timedelta, timezone

from fastapi import Depends

from packages.auth import auth_scheme
from exceptions import ConflictError, NotFoundError, TooManyRequestsError

from . import repository


async def valid_anime_for_update(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Validates that the anime exists and is eligible for update (5-minute cooldown)."""
    anime = await repository.get_anime_by_id(anime_id)

    if not anime or not anime["last_scraped_at"]:
        raise NotFoundError(
            "Anime not found or not yet created. "
            "Use GET /animes/info/{anime_id} to create it first."
        )

    current_time = datetime.now(timezone.utc)
    last_scraped = anime["last_scraped_at"]
    if last_scraped.tzinfo is None:
        last_scraped = last_scraped.replace(tzinfo=timezone.utc)
    cooldown_minutes = 5

    time_diff = current_time - last_scraped
    if time_diff < timedelta(minutes=cooldown_minutes):
        remaining_seconds = int(
            (timedelta(minutes=cooldown_minutes) - time_diff).total_seconds()
        )
        raise TooManyRequestsError(
            f"Anime was updated recently. "
            f"Please wait {remaining_seconds} seconds before updating."
        )

    return {
        "anime_id": anime_id,
        "user_id": current_user["id"],
    }


async def valid_anime_id(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Validates that the anime exists and returns the required data."""
    anime = await repository.get_anime_by_id(anime_id)
    if not anime:
        raise NotFoundError(f"Anime {anime_id} not found")

    return {
        "anime_id": anime_id,
        "user_id": current_user["id"],
    }


async def anime_is_saved_by_user(
    anime_data: dict = Depends(valid_anime_id),
) -> dict:
    """Verifies that the user has the anime saved."""
    saved = await repository.get_user_saved_anime(
        anime_data["user_id"], anime_data["anime_id"]
    )
    if not saved:
        raise NotFoundError("Anime not saved by user")
    return anime_data


async def anime_not_saved_by_user(
    anime_data: dict = Depends(valid_anime_id),
) -> dict:
    """Verifies that the user does NOT have the anime saved."""
    saved = await repository.get_user_saved_anime(
        anime_data["user_id"], anime_data["anime_id"]
    )
    if saved:
        raise ConflictError("Anime already saved by user")
    return anime_data


async def user_not_saved_anime(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Verifies the user has not saved the anime without requiring it to exist in the DB first."""
    saved = await repository.get_user_saved_anime(current_user["id"], anime_id)
    if saved:
        raise ConflictError("Anime already saved by user")

    return {
        "anime_id": anime_id,
        "user_id": current_user["id"],
    }
