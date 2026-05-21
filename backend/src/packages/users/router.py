from fastapi import APIRouter, Depends

from packages.auth import auth_scheme
from responses import SuccessResponse

from .schemas import UserUpdateInfo
from .service import (
    check_username_controller,
    get_avatars_controller,
    get_me_controller,
    get_user_statistics_controller,
    get_users_controller,
    update_user_controller,
)

users_router = APIRouter()


@users_router.get("")
async def get_users(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_users_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="Users retrieved")


@users_router.get("/me")
async def get_me(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_me_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="User retrieved")


@users_router.get("/username/{username}")
async def check_username(
    username: str,
    current_user: dict = Depends(auth_scheme),
):
    payload = await check_username_controller(username)
    return SuccessResponse(payload=payload, message="Username checked")


@users_router.put("")
async def update_user(
    user_info: UserUpdateInfo,
    current_user: dict = Depends(auth_scheme),
):
    payload = await update_user_controller(user_info, current_user["id"])
    return SuccessResponse(payload=payload, message="User updated")


@users_router.get("/avatars")
async def get_avatars(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_avatars_controller()
    return SuccessResponse(payload=payload, message="Avatars retrieved")


@users_router.get("/statistics")
async def get_user_statistics(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_user_statistics_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="User statistics retrieved")
