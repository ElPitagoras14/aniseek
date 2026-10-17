from fastapi import APIRouter, Depends

from packages.auth import auth_scheme
from responses import SuccessResponse

from .responses import (
    AnimeOut,
    InEmissionAnimeListOut,
    SavedAnimeResultListOut,
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


@animes_router.get("/search", response_model=SearchAnimeResultListOut)
async def search_animes(
    query: str,
    current_user: dict = Depends(auth_scheme),
):
    payload = await search_anime_controller(query, current_user["id"])
    return SuccessResponse(payload=payload, message="Anime searched")


@animes_router.get("/saved", response_model=SavedAnimeResultListOut)
async def get_saved_animes(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_saved_animes_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="Saved animes retrieved")


@animes_router.get("/in-emission", response_model=InEmissionAnimeListOut)
async def get_in_emission_animes(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_in_emission_animes_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="In-emission animes retrieved")


@animes_router.get("/{anime_id}", response_model=AnimeOut)
async def get_anime(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_anime_controller(anime_id, current_user["id"])
    return SuccessResponse(payload=payload, message="Anime retrieved")


@animes_router.put("/{anime_id}", response_model=AnimeOut)
async def update_anime(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
):
    payload = await update_anime_controller(anime_id, current_user["id"])
    return SuccessResponse(payload=payload, message="Anime updated successfully")


@animes_router.put("/{anime_id}/save", response_model=SuccessResponse)
async def save_anime(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
):
    await save_anime_controller(anime_id, current_user["id"])
    return SuccessResponse(payload=None, message="Anime saved successfully")


@animes_router.put("/{anime_id}/unsave", response_model=SuccessResponse)
async def unsave_anime(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
):
    await unsave_anime_controller(anime_id, current_user["id"])
    return SuccessResponse(payload=None, message="Anime unsaved successfully")
