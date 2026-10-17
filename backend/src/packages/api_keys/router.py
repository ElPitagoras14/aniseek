from uuid import UUID

from fastapi import APIRouter, Depends

from packages.auth import auth_scheme, require_role
from responses import SuccessResponse

from .service import (
    generate_api_key_controller,
    get_own_api_key_controller,
    list_api_keys_controller,
    revoke_api_key_controller,
)

# Managing a key is a UI action: these routes use the web session, never the
# API key itself (design D6).
api_keys_router = APIRouter()


@api_keys_router.get("/me")
async def get_own_api_key(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_own_api_key_controller(current_user)
    return SuccessResponse(payload=payload, message="API key retrieved")


@api_keys_router.post("/me")
async def generate_api_key(
    current_user: dict = Depends(auth_scheme),
):
    payload = await generate_api_key_controller(current_user)
    return SuccessResponse(payload=payload, message="API key generated")


@api_keys_router.delete("/me")
async def revoke_own_api_key(
    current_user: dict = Depends(auth_scheme),
):
    await revoke_api_key_controller(current_user, current_user["id"])
    return SuccessResponse(payload=None, message="API key revoked")


@api_keys_router.get("")
async def list_api_keys(
    current_user: dict = Depends(require_role("owner")),
):
    payload = await list_api_keys_controller()
    return SuccessResponse(payload=payload, message="API keys retrieved")


@api_keys_router.delete("/{user_id}")
async def revoke_api_key(
    user_id: UUID,
    current_user: dict = Depends(require_role("owner")),
):
    await revoke_api_key_controller(current_user, str(user_id))
    return SuccessResponse(payload=None, message="API key revoked")
