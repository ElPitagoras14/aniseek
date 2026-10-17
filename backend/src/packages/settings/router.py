from fastapi import APIRouter, Depends

from packages.auth import require_role
from responses import SuccessResponse

from .schemas import SettingsUpdateInfo
from .service import get_settings_controller, update_settings_controller

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
