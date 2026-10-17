"""Provider-namespaced anime ids, used only by the MCP (mcp-server, design D6).
Phase 2 resolves the provider here; the tools do not change."""

import re

from mcp.server.mcpserver.exceptions import ToolError

SUPPORTED_PROVIDERS = ("animeav1",)

_ID_PATTERN = re.compile(r"^(?P<provider>[a-z0-9]+):(?P<slug>[a-z0-9-]+)$")


def parse_anime_id(anime_id: str) -> str:
    """`animeav1:one-piece` -> `one-piece`. Rejects a missing or unsupported
    provider and any other shape."""
    supported = ", ".join(SUPPORTED_PROVIDERS)
    match = _ID_PATTERN.match(anime_id)
    if not match:
        raise ToolError(
            f"Invalid anime id {anime_id!r}: expected '<provider>:<slug>', "
            f"for example 'animeav1:one-piece'. Supported providers: {supported}"
        )
    if match["provider"] not in SUPPORTED_PROVIDERS:
        raise ToolError(
            f"Unsupported provider {match['provider']!r} in {anime_id!r}. "
            f"Supported providers: {supported}"
        )
    return match["slug"]


def format_anime_id(slug: str) -> str:
    return f"{SUPPORTED_PROVIDERS[0]}:{slug}"
