from fastapi import APIRouter, Depends

from packages.auth import auth_scheme
from utils.responses import SuccessResponse

from .dependencies import (
    anime_is_saved_by_user,
    user_not_saved_anime,
    valid_anime_for_update,
    valid_anime_id,
)
from .responses import (
    AnimeOut,
    InEmissionAnimeListOut,
    SearchAnimeResultListOut,
)
from .service import (
    get_anime_controller,
    get_in_emission_animes_controller,
    get_saved_animes_controller,
    save_anime_controller,
    search_anime_controller,
    unsave_anime_controller,
    update_anime_controller,
)

animes_router = APIRouter()


@animes_router.get(
    "/search",
    response_model=SearchAnimeResultListOut,
    summary="Search animes",
    description="Search for animes by query string",
)
async def search_animes(
    query: str,
    current_user: dict = Depends(auth_scheme),
):
    data = await search_anime_controller(query, current_user["id"])
    return SuccessResponse(payload=data, message="Anime searched")


@animes_router.get(
    "/saved",
    response_model=SearchAnimeResultListOut,
    summary="Get saved animes",
    description="Get all animes saved by the current user",
)
async def get_saved_animes(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_saved_animes_controller(current_user["id"])
    return SuccessResponse(payload=data, message="Saved animes retrieved")


@animes_router.get(
    "/in-emission",
    response_model=InEmissionAnimeListOut,
    summary="Get in-emission animes",
    description="Get animes that are currently airing",
)
async def get_in_emission_animes(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_in_emission_animes_controller(current_user["id"])
    return SuccessResponse(payload=data, message="In-emission animes retrieved")


@animes_router.get(
    "/{anime_id}",
    response_model=AnimeOut,
    summary="Get anime details",
    description="Retrieve detailed information about an anime by ID",
)
async def get_anime(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
):
    data = await get_anime_controller(anime_id, current_user["id"])
    return SuccessResponse(payload=data, message="Anime retrieved")


@animes_router.put(
    "/{anime_id}",
    response_model=AnimeOut,
    summary="Update anime info",
    description="Force update anime information (5 min cooldown required)",
    status_code=200,
)
async def update_anime(
    anime_data: dict = Depends(valid_anime_for_update),
):
    anime_id = anime_data["anime_id"]
    user_id = anime_data["user_id"]

    data = await update_anime_controller(anime_id, user_id)
    return SuccessResponse(payload=data, message="Anime updated successfully")


@animes_router.put(
    "/{anime_id}/save",
    response_model=SuccessResponse,
    summary="Save anime",
    description="Save an anime to user's list",
    status_code=200,
)
async def save_anime(
    anime_data: dict = Depends(user_not_saved_anime),
):
    await save_anime_controller(anime_data["anime_id"], anime_data["user_id"])
    return SuccessResponse(payload=None, message="Anime saved successfully")


@animes_router.put(
    "/{anime_id}/unsave",
    response_model=SuccessResponse,
    summary="Unsave anime",
    description="Remove an anime from user's saved list",
    status_code=200,
)
async def unsave_anime(
    anime_data: dict = Depends(anime_is_saved_by_user),
):
    await unsave_anime_controller(anime_data["anime_id"], anime_data["user_id"])
    return SuccessResponse(payload=None, message="Anime unsaved successfully")
