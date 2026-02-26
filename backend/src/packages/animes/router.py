import json
from fastapi.responses import FileResponse, StreamingResponse
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends

from utils.responses import SuccessResponse
from packages.auth import auth_scheme
from .dependencies import (
    valid_anime_id,
    valid_episode_by_number,
    anime_not_saved_by_user,
    anime_is_saved_by_user,
    valid_downloaded_episode,
    valid_anime_for_update,
)
from .service import (
    delete_anime_storage_controller,
    delete_download_episode_controller,
    download_anime_episode_bulk_controller,
    download_anime_episode_controller,
    get_animes_storage_controller,
    get_download_episodes_controller,
    get_downloaded_animes_controller,
    get_in_emission_animes_controller,
    get_last_downloaded_episodes_controller,
    get_saved_animes_controller,
    save_anime_controller,
    search_anime_controller,
    get_anime_controller,
    unsave_anime_controller,
    update_anime_controller,
)
from .responses import (
    AnimeDownloadInfoListOut,
    AnimeOut,
    DownloadTaskListOut,
    DownloadTaskOut,
    EpisodeDownloadListOut,
    SearchAnimeResultListOut,
    InEmissionAnimeListOut,
)
from .config import anime_settings

REDIS_URL = anime_settings.REDIS_URL

animes_router = APIRouter()


@animes_router.get(
    "/info/{anime_id}",
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
    "/info/{anime_id}",
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


@animes_router.put(
    "/save/{anime_id}",
    response_model=SuccessResponse,
    summary="Save anime",
    description="Save an anime to user's list",
    status_code=200,
)
async def save_anime(
    anime_data: dict = Depends(anime_not_saved_by_user),
):
    await save_anime_controller(anime_data["anime_id"], anime_data["user_id"])
    return SuccessResponse(payload=None, message="Anime saved successfully")


@animes_router.put(
    "/unsave/{anime_id}",
    response_model=SuccessResponse,
    summary="Unsave anime",
    description="Remove an anime from user's saved list",
    status_code=200,
)
async def unsave_anime(
    anime_data: dict = Depends(anime_is_saved_by_user),
):
    await unsave_anime_controller(
        anime_data["anime_id"], anime_data["user_id"]
    )
    return SuccessResponse(payload=None, message="Anime unsaved successfully")


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
    return SuccessResponse(
        payload=data, message="In-emission animes retrieved"
    )


@animes_router.get(
    "/download",
    response_model=EpisodeDownloadListOut,
    summary="Get download episodes",
    description="Get list of downloaded episodes",
)
async def get_download_episodes(
    anime_id: str | None = None,
    limit: int = 10,
    page: int = 1,
    current_user: dict = Depends(auth_scheme),
):
    data = await get_download_episodes_controller(
        current_user["id"], anime_id, limit, page
    )
    return SuccessResponse(payload=data, message="Downloads retrieved")


@animes_router.get(
    "/download/last",
    response_model=EpisodeDownloadListOut,
    summary="Get last downloaded episodes",
    description="Get recently downloaded episodes",
)
async def get_last_downloaded_episodes(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_last_downloaded_episodes_controller(current_user["id"])
    return SuccessResponse(
        payload=data, message="Last downloaded episodes retrieved"
    )


@animes_router.get(
    "/download/anime",
    response_model=AnimeDownloadInfoListOut,
    summary="Get downloaded animes",
    description="Get list of animes with downloads",
)
async def get_downloaded_animes(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_downloaded_animes_controller(current_user["id"])
    return SuccessResponse(payload=data, message="Downloaded animes retrieved")


@animes_router.get(
    "/stream/download",
    summary="Stream download status",
    description="SSE stream for download job status updates",
)
async def get_download_status(job_ids: str):
    ids = set(job_ids.split(","))

    async def event_generator():
        redis_sub = aioredis.from_url(f"{REDIS_URL}/2")
        pubsub = redis_sub.pubsub()
        await pubsub.subscribe("job_updates")

        async for message in pubsub.listen():
            if message["type"] == "message":
                payload = json.loads(message["data"])
                if payload["job_id"] in ids:
                    data = json.dumps(payload)
                    yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@animes_router.get(
    "/download/episode/{episode_id}",
    summary="Download episode file",
    description="Get the downloaded episode file",
)
async def get_download_episode(
    episode_data: dict = Depends(valid_downloaded_episode),
):
    return FileResponse(
        episode_data["file_path"],
        media_type="video/mp4",
        headers={
            "Content-Disposition": "attachment; "
            + f"filename={episode_data['filename']}"
        },
    )


@animes_router.post(
    "/download/single/{anime_id}/{episode_number}",
    response_model=DownloadTaskOut,
    summary="Download single episode",
    description="Download a single anime episode",
    status_code=201,
)
async def download_anime_episode(
    episode_data: dict = Depends(valid_episode_by_number),
    force_download: bool = False,
    current_user: dict = Depends(auth_scheme),
):
    data = await download_anime_episode_controller(
        episode_data["episode_id"],
        force_download,
        current_user["id"],
    )
    return SuccessResponse(
        payload=data, message="Anime download enqueued successfully"
    )


@animes_router.delete(
    "/download/single/{anime_id}/{episode_number}",
    response_model=SuccessResponse,
    summary="Delete downloaded episode",
    description="Delete a downloaded episode",
    status_code=200,
)
async def delete_download_episode(
    episode_data: dict = Depends(valid_episode_by_number),
    current_user: dict = Depends(auth_scheme),
):
    await delete_download_episode_controller(
        episode_data["episode_id"],
        current_user["id"],
    )
    return SuccessResponse(
        payload=None, message="Download episode deleted successfully"
    )


@animes_router.post(
    "/download/bulk/{anime_id}",
    response_model=DownloadTaskListOut,
    summary="Bulk download episodes",
    description="Download multiple episodes of an anime",
    status_code=201,
)
async def download_anime_episode_bulk(
    anime_id: str,
    episodes: list[int],
    current_user: dict = Depends(auth_scheme),
    anime_data: dict = Depends(valid_anime_id),
):
    data = await download_anime_episode_bulk_controller(
        anime_data["anime_id"],
        episodes,
        current_user["id"],
    )
    return SuccessResponse(
        payload=data, message="Anime downloaded successfully"
    )


@animes_router.get(
    "/storage",
    response_model=AnimeDownloadInfoListOut,
    summary="Get storage info",
    description="Get anime storage usage information",
)
async def get_animes_storage(
    limit: int = 10,
    page: int = 1,
    current_user: dict = Depends(auth_scheme),
):
    data = await get_animes_storage_controller(limit, page)
    return SuccessResponse(payload=data, message="Animes storage retrieved")


@animes_router.delete(
    "/storage/{anime_id}",
    response_model=SuccessResponse,
    summary="Delete anime storage",
    description="Delete all downloaded episodes for an anime",
    status_code=200,
)
async def delete_anime_storage(
    anime_data: dict = Depends(valid_anime_id),
    current_user: dict = Depends(auth_scheme),
):
    await delete_anime_storage_controller(
        anime_data["anime_id"], current_user["id"]
    )
    return SuccessResponse(
        payload=None, message="Anime storage deleted successfully"
    )
