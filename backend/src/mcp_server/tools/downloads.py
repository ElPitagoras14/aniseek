"""Download tools (mcp-server, design D7 and D8)."""

from typing import Annotated

from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from packages.animes.service import assert_anime_exists
from packages.episodes.service import (
    download_anime_episode_bulk_controller,
    get_episodes_download_status,
)

from ..ids import format_anime_id, parse_anime_id
from ..schemas import (
    DownloadRequestResult,
    DownloadStatusResult,
    EpisodeDownloadStatus,
    EpisodeRequestResult,
    episode_status,
)
from ..server import current_user, tool

# Episodes a single download_episodes call may enqueue. Not a quota: it keeps
# one call from queueing a whole series by mistake.
MCP_DOWNLOAD_CAP = 25

EpisodeNumbers = Annotated[
    list[Annotated[int, Field(ge=1)]],
    Field(min_length=1, description="Episode numbers"),
]


def _unique(numbers: list[int]) -> list[int]:
    return list(dict.fromkeys(numbers))


@tool(read_only=False, title="Download episodes")
async def download_episodes(
    anime_id: str, episodes: EpisodeNumbers, ctx: Context
) -> DownloadRequestResult:
    """Request the download of episodes of an anime. Episodes the user
    already requested are skipped and do not count; at most 25 other episodes
    per call."""
    slug = parse_anime_id(anime_id)
    user_id = current_user()["id"]
    numbers = _unique(episodes)

    await assert_anime_exists(slug)
    known = await get_episodes_download_status(slug, numbers, user_id)
    remaining = [n for n in numbers if not known.get(n, {}).get("requested_by_user")]
    if len(remaining) > MCP_DOWNLOAD_CAP:
        raise ToolError(
            f"Too many episodes: {len(remaining)} not yet downloaded, at most "
            f"{MCP_DOWNLOAD_CAP} per call. Split the request into calls of up to "
            f"{MCP_DOWNLOAD_CAP} episodes."
        )

    result = await download_anime_episode_bulk_controller(slug, numbers, user_id)
    by_number = {item.episode_number: item for item in result.items}
    states = [
        EpisodeRequestResult(
            number=n,
            state="enqueued" if by_number[n].success else by_number[n].reason,
        )
        for n in numbers
    ]
    return DownloadRequestResult(
        anime_id=format_anime_id(slug),
        episodes=states,
        enqueued=sum(1 for s in states if s.state == "enqueued"),
    )


@tool(read_only=True, title="Get download status")
async def get_download_status(
    anime_id: str, episodes: EpisodeNumbers, ctx: Context
) -> DownloadStatusResult:
    """Current download status of episodes of an anime, including the ones
    that already finished, and whether the user requested each one."""
    slug = parse_anime_id(anime_id)
    numbers = _unique(episodes)

    await assert_anime_exists(slug)
    known = await get_episodes_download_status(slug, numbers, current_user()["id"])
    return DownloadStatusResult(
        anime_id=format_anime_id(slug),
        episodes=[
            EpisodeDownloadStatus(
                number=n,
                status=episode_status(known[n]["status"]),
                requested_by_user=known[n]["requested_by_user"],
            )
            if n in known
            else EpisodeDownloadStatus(
                number=n, status="not_found", requested_by_user=False
            )
            for n in numbers
        ],
    )
