"""ASGI entry point of /api/mcp (mcp-server, design D2): instance switch,
then API key, then the SDK."""

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import Receive, Scope, Send

from database.client import engine
from packages.auth import api_key_scheme
from packages.settings.repository import is_mcp_enabled

from .server import USER_SCOPE_KEY, handle_mcp_request


class McpGate:
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Read on every request, so the switch takes effect immediately and
        # across replicas. Checked before the key: with the MCP off the
        # endpoint answers as if it did not exist.
        async with engine.connect() as conn:
            enabled = await is_mcp_enabled(conn)
        if not enabled:
            response = JSONResponse({"detail": "Not Found"}, status_code=404)
            await response(scope, receive, send)
            return

        # FastAPI's exception handlers do not cover this route: the gate
        # renders its own errors.
        try:
            current_user = await api_key_scheme(Request(scope, receive))
        except HTTPException as e:
            response = JSONResponse(
                {"detail": e.detail},
                status_code=e.status_code,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return

        scope[USER_SCOPE_KEY] = current_user
        await handle_mcp_request(scope, receive, send)
