import json

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse

from packages.auth import auth_scheme
from packages.animes.dependencies import valid_anime_id
from utils.responses import SuccessResponse

from .config import episodes_settings
from .dependencies import (
    valid_downloaded_episode_public,
    valid_episode_by_number,
)
from .responses import (
    AnimeDownloadInfoListOut,
    DownloadTaskListOut,
    DownloadTaskOut,
    EpisodeDownloadListOut,
)
from .service import (
    delete_anime_storage_controller,
    delete_download_episode_controller,
    download_anime_episode_bulk_controller,
    download_anime_episode_controller,
    get_animes_storage_controller,
    get_download_episodes_controller,
    get_downloaded_animes_controller,
    get_last_downloaded_episodes_controller,
)

REDIS_URL = episodes_settings.REDIS_URL

episodes_router = APIRouter()


@episodes_router.get(
    "/downloads",
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


@episodes_router.get(
    "/downloads/last",
    response_model=EpisodeDownloadListOut,
    summary="Get last downloaded episodes",
    description="Get recently downloaded episodes",
)
async def get_last_downloaded_episodes(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_last_downloaded_episodes_controller(current_user["id"])
    return SuccessResponse(payload=data, message="Last downloaded episodes retrieved")


@episodes_router.get(
    "/downloads/animes",
    response_model=AnimeDownloadInfoListOut,
    summary="Get downloaded animes",
    description="Get list of animes with downloads",
)
async def get_downloaded_animes(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_downloaded_animes_controller(current_user["id"])
    return SuccessResponse(payload=data, message="Downloaded animes retrieved")


@episodes_router.get(
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


@episodes_router.delete(
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
    await delete_anime_storage_controller(anime_data["anime_id"], current_user["id"])
    return SuccessResponse(payload=None, message="Anime storage deleted successfully")


@episodes_router.get(
    "/stream/status",
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


@episodes_router.get(
    "/{episode_id}/file",
    summary="Download episode file",
    description="Get the downloaded episode file",
)
async def get_download_episode(
    episode_data: dict = Depends(valid_downloaded_episode_public),
):
    return FileResponse(
        episode_data["file_path"],
        media_type="video/mp4",
        headers={
            "Content-Disposition": "attachment; "
            + f"filename={episode_data['filename']}"
        },
    )


@episodes_router.post(
    "/{anime_id}/{episode_number}/download",
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
    return SuccessResponse(payload=data, message="Anime download enqueued successfully")


@episodes_router.delete(
    "/{anime_id}/{episode_number}/download",
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


@episodes_router.post(
    "/{anime_id}/download/bulk",
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
    return SuccessResponse(payload=data, message="Anime downloaded successfully")
