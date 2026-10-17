from fastapi import APIRouter, Depends

from packages.auth import auth_scheme, require_role
from responses import SuccessResponse

from .schemas import McpSettingsUpdateInfo, SettingsUpdateInfo
from .service import (
    get_mcp_settings_controller,
    get_settings_controller,
    update_mcp_settings_controller,
    update_settings_controller,
)

settings_router = APIRouter()


@settings_router.get("")
async def get_settings(
    current_user: dict = Depends(require_role("admin")),
):
    payload = await get_settings_controller()
    return SuccessResponse(payload=payload, message="Settings retrieved")


@settings_router.put("")
async def update_settings(
    settings_info: SettingsUpdateInfo,
    current_user: dict = Depends(require_role("admin")),
):
    payload = await update_settings_controller(settings_info, current_user["id"])
    return SuccessResponse(payload=payload, message="Settings updated")


@settings_router.get("/mcp")
async def get_mcp_settings(
    current_user: dict = Depends(auth_scheme),
):
    # Any user: Profile shows whether agents can connect.
    payload = await get_mcp_settings_controller()
    return SuccessResponse(payload=payload, message="MCP settings retrieved")


@settings_router.put("/mcp")
async def update_mcp_settings(
    settings_info: McpSettingsUpdateInfo,
    current_user: dict = Depends(require_role("owner")),
):
    payload = await update_mcp_settings_controller(settings_info, current_user["id"])
    return SuccessResponse(payload=payload, message="MCP settings updated")
