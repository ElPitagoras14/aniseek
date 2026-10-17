"""Tools that change the user's library or the instance's files."""

from mcp.server.mcpserver import Context

from packages.animes.service import (
    load_anime_detail,
    refresh_anime as refresh_anime_service,
    save_anime_controller,
    unsave_anime_controller,
)
from packages.episodes.service import delete_anime_storage_controller

from ..ids import format_anime_id, parse_anime_id
from ..schemas import AnimeDetail, FilesDeleted, SavedState
from ..server import current_user, tool
from .catalog import anime_detail


@tool(read_only=False, open_world=True, title="Save anime")
async def save_anime(anime_id: str, ctx: Context) -> SavedState:
    """Add an anime to the user's saved list."""
    slug = parse_anime_id(anime_id)
    await save_anime_controller(slug, current_user()["id"])
    return SavedState(anime_id=format_anime_id(slug), is_saved=True)


@tool(read_only=False, title="Unsave anime")
async def unsave_anime(anime_id: str, ctx: Context) -> SavedState:
    """Remove an anime from the user's saved list."""
    slug = parse_anime_id(anime_id)
    await unsave_anime_controller(slug, current_user()["id"])
    return SavedState(anime_id=format_anime_id(slug), is_saved=False)


@tool(read_only=False, open_world=True, title="Refresh anime")
async def refresh_anime(anime_id: str, ctx: Context) -> AnimeDetail:
    """Sync an anime again from the provider to pick up new episodes. Allowed
    once every 5 minutes per anime."""
    slug = parse_anime_id(anime_id)
    await refresh_anime_service(slug)
    return anime_detail(await load_anime_detail(slug, current_user()["id"]))


@tool("admin", read_only=False, destructive=True, title="Delete anime files")
async def delete_anime_files(anime_id: str, ctx: Context) -> FilesDeleted:
    """Delete every downloaded episode file of an anime from the instance's
    storage, for all users. Cannot be undone."""
    slug = parse_anime_id(anime_id)
    await delete_anime_storage_controller(slug, current_user()["id"])
    return FilesDeleted(anime_id=format_anime_id(slug), deleted=True)
