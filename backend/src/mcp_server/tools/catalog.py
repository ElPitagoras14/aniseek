"""Read-only tools over the catalog and the user's library."""

from typing import Annotated, Literal

from mcp.server.mcpserver import Context
from pydantic import Field

from packages.animes.service import (
    ensure_anime_scraped,
    get_in_emission_animes_controller,
    get_saved_animes_controller,
    load_anime_detail,
    search_anime_controller,
)
from packages.episodes.service import (
    get_animes_storage_controller,
    get_download_episodes_controller,
)
from packages.users.service import get_user_statistics_controller

from ..ids import format_anime_id, parse_anime_id
from ..schemas import (
    AiringAnime,
    AiringAnimeList,
    AnimeDetail,
    AnimeSearchResult,
    AnimeStorage,
    AnimeSummary,
    DownloadRecord,
    DownloadRecordList,
    EpisodeState,
    RelatedAnime,
    SavedAnime,
    SavedAnimeList,
    StorageUsage,
    UserStats,
    episode_status,
)
from ..server import current_user, tool

Weekday = Literal[
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]
Page = Annotated[int, Field(ge=1, description="1-based page number")]
PageSize = Annotated[int, Field(ge=1, le=100, description="Items per page")]


def anime_detail(anime_db: dict) -> AnimeDetail:
    """Builds the MCP view of an anime from `load_anime_detail`."""
    saved = anime_db["saved_info"]
    return AnimeDetail(
        id=format_anime_id(anime_db["id"]),
        title=anime_db["title"],
        type=anime_db["type"],
        description=anime_db["description"],
        genres=anime_db["genres"],
        is_finished=anime_db["is_finished"],
        week_day=anime_db["week_day"],
        is_saved=saved["is_saved"],
        saved_at=saved["save_date"],
        last_synced_at=anime_db["last_scraped_at"],
        related=[
            RelatedAnime(
                id=format_anime_id(rel["related_anime_id"]),
                title=rel["related_title"],
                relation=rel["type_related_name"],
            )
            for rel in anime_db["relations"]
        ],
        episodes=[
            EpisodeState(
                number=ep["ep_number"],
                status=episode_status(ep["status"]),
                requested_by_user=ep["is_user_downloaded"],
            )
            for ep in anime_db["episodes"]
        ],
    )


@tool(read_only=True, open_world=True, title="Search anime")
async def search_anime(
    query: Annotated[str, Field(min_length=1, description="Text to search for")],
    ctx: Context,
) -> AnimeSearchResult:
    """Search the catalog provider for anime by title."""
    result = await search_anime_controller(query, current_user()["id"])
    items = [
        AnimeSummary(
            id=format_anime_id(a.id), title=a.title, type=a.type, is_saved=a.is_saved
        )
        for a in result.items
    ]
    return AnimeSearchResult(items=items, total=len(items))


@tool(read_only=True, open_world=True, title="Get anime")
async def get_anime(anime_id: str, ctx: Context) -> AnimeDetail:
    """Get an anime's details, related anime and every episode with its
    download status. Fetches it from the provider the first time."""
    slug = parse_anime_id(anime_id)
    await ensure_anime_scraped(slug)
    return anime_detail(await load_anime_detail(slug, current_user()["id"]))


@tool(read_only=True, title="List saved anime")
async def list_saved(ctx: Context) -> SavedAnimeList:
    """List the anime the user has saved."""
    result = await get_saved_animes_controller(current_user()["id"])
    items = [
        SavedAnime(
            id=format_anime_id(a.id),
            title=a.title,
            type=a.type,
            is_finished=a.is_finished,
            saved_at=a.save_date,
        )
        for a in result.items
    ]
    return SavedAnimeList(items=items, total=len(items))


@tool(read_only=True, title="List airing anime")
async def list_airing(
    ctx: Context,
    week_day: Annotated[
        Weekday | None, Field(description="Only anime airing on this weekday")
    ] = None,
) -> AiringAnimeList:
    """List the user's saved anime that are still airing, with the weekday a
    new episode comes out."""
    result = await get_in_emission_animes_controller(current_user()["id"])
    items = [
        AiringAnime(id=format_anime_id(a.id), title=a.title, week_day=a.week_day)
        for a in result.items
        if week_day is None or a.week_day == week_day
    ]
    return AiringAnimeList(items=items, total=len(items))


@tool(read_only=True, title="List downloads")
async def list_downloads(
    ctx: Context,
    anime_id: Annotated[
        str | None, Field(description="Only downloads of this anime")
    ] = None,
    query: Annotated[str | None, Field(description="Filter by anime title")] = None,
    page: Page = 1,
    page_size: PageSize = 20,
) -> DownloadRecordList:
    """List the user's download history, most recent first."""
    slug = parse_anime_id(anime_id) if anime_id else None
    result = await get_download_episodes_controller(
        current_user()["id"], slug, page_size, page, query.strip() if query else None
    )
    items = [
        DownloadRecord(
            anime_id=format_anime_id(d.anime_id),
            anime_title=d.title,
            episode_number=d.episode_number,
            status=episode_status(d.status),
            size_bytes=d.size,
            requested_at=d.downloaded_at,
        )
        for d in result.items
    ]
    return DownloadRecordList(items=items, total=result.total, page=page)


@tool(read_only=True, title="Get storage usage")
async def get_storage_usage(
    ctx: Context,
    query: Annotated[str | None, Field(description="Filter by anime title")] = None,
    page: Page = 1,
    page_size: PageSize = 20,
) -> StorageUsage:
    """Disk space used by downloaded episodes, per anime and in total."""
    result = await get_animes_storage_controller(page_size, page, query)
    return StorageUsage(
        items=[
            AnimeStorage(
                anime_id=format_anime_id(a.id), title=a.title, size_bytes=a.size
            )
            for a in result.items
        ],
        total=result.total,
        total_size_bytes=result.total_size,
        page=page,
    )


@tool(read_only=True, title="Get user stats")
async def get_stats(ctx: Context) -> UserStats:
    """Counts of the user's saved anime, downloaded episodes and saved anime
    still airing."""
    stats = await get_user_statistics_controller(current_user()["id"])
    return UserStats(
        saved_animes=stats.saved_animes,
        downloaded_episodes=stats.downloaded_episodes,
        airing_saved_animes=stats.in_emission_animes,
    )
