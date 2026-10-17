"""The MCP server instance and the helper every tool registers through
(mcp-server, design D3 and D4)."""

import functools
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any, ParamSpec, TypeVar

from loguru import logger
from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ListToolsResult, ToolAnnotations
from starlette.requests import Request

from exceptions import AppError
from packages.auth import assert_min_role, role_rank
from packages.auth.roles import ROLE_RANK

# Key under which McpGate leaves the authenticated user in the ASGI scope. The
# SDK serves stateless requests from a task group opened in the lifespan, so a
# contextvar set by the gate would not reach the handlers; the scope does,
# because every handler receives the HTTP request.
USER_SCOPE_KEY = "aniseek.current_user"

# Minimum role of each registered tool, by name.
TOOL_MIN_ROLE: dict[str, str] = {}

_current_user: ContextVar[dict] = ContextVar("mcp_current_user")


def _user_from_request(request: Request | None) -> dict:
    user = request.scope.get(USER_SCOPE_KEY) if request is not None else None
    if user is None:
        # McpGate always sets it: reaching here means the server was served
        # without the gate.
        raise ToolError("Unauthenticated MCP request")
    return user


def current_user() -> dict:
    """The user of the tool call being executed (set by the `tool` wrapper)."""
    return _current_user.get()


def can_use(user: dict, tool_name: str) -> bool:
    min_role = TOOL_MIN_ROLE.get(tool_name)
    return min_role is not None and role_rank(user["role"]) >= ROLE_RANK[min_role]


class AniseekMCPServer(MCPServer):
    async def _handle_list_tools(self, ctx, params) -> ListToolsResult:
        # Only the tools the caller's current role can use (design D4).
        user = _user_from_request(ctx.request)
        tools = await self.list_tools()
        return ListToolsResult(tools=[t for t in tools if can_use(user, t.name)])


server = AniseekMCPServer(
    name="aniseek",
    title="Ani Seek",
    instructions=(
        "Search, organize and download anime in an Ani Seek instance on behalf "
        "of the API key's user. Anime ids have the form '<provider>:<slug>', "
        "for example 'animeav1:one-piece'."
    ),
)

P = ParamSpec("P")
R = TypeVar("R")


def tool(
    min_role: str = "member",
    *,
    read_only: bool,
    destructive: bool = False,
    open_world: bool = False,
    title: str | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Registers an async tool with its minimum role and MCP annotations.

    The tool must declare a `ctx: Context` parameter (the SDK injects it). The
    wrapper checks the caller's current role before the body runs, exposes
    the user through `current_user()`, and turns an `AppError` into a tool
    error carrying its message (design D10)."""
    if min_role not in ROLE_RANK:
        raise ValueError(f"Unknown role: {min_role!r}")

    def decorator(fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            ctx = next(v for v in kwargs.values() if isinstance(v, Context))
            user = _user_from_request(ctx.request_context.request)
            token = _current_user.set(user)
            try:
                assert_min_role(user, min_role)
                return await fn(*args, **kwargs)
            except AppError as e:
                raise ToolError(e.message) from e
            finally:
                _current_user.reset(token)

        TOOL_MIN_ROLE[fn.__name__] = min_role
        server.add_tool(
            wrapper,
            title=title,
            annotations=ToolAnnotations(
                read_only_hint=read_only,
                destructive_hint=destructive,
                open_world_hint=open_world,
            ),
        )
        return wrapper

    return decorator


@asynccontextmanager
async def mcp_lifespan() -> AsyncIterator[None]:
    """Runs the MCP session manager. A manager can only run once, so each run
    builds a fresh one: stateless, JSON responses (design D3). DNS rebinding
    protection stays off: every request carries an API key, and the allowed
    hosts depend on how the instance is exposed."""
    server.streamable_http_app(
        json_response=True,
        stateless_http=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False
        ),
    )
    async with server.session_manager.run():
        logger.info("MCP session manager started")
        yield


async def handle_mcp_request(scope: Any, receive: Any, send: Any) -> None:
    await server.session_manager.handle_request(scope, receive, send)
