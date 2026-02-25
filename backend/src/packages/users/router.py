from fastapi import APIRouter, Depends

from utils.responses import SuccessResponse
from packages.auth import auth_scheme
from .service import (
    check_username_controller,
    get_avatars_controller,
    get_me_controller,
    get_user_statistics_controller,
    get_users_controller,
    update_user_controller,
)
from .schemas import UserInfo

users_router = APIRouter()


@users_router.get("")
async def get_users(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_users_controller(current_user["id"])
    return SuccessResponse(payload=data, message="Users retrieved")


@users_router.get("/me")
async def get_me(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_me_controller(current_user["id"])
    return SuccessResponse(payload=data, message="User retrieved")


@users_router.get("/username/{username}")
async def check_username(
    username: str,
):
    data = await check_username_controller(username)
    return SuccessResponse(payload=data, message="Username checked")


@users_router.put("")
async def update_user(
    user_info: UserInfo,
    current_user: dict = Depends(auth_scheme),
):
    data = await update_user_controller(user_info, current_user["id"])
    return SuccessResponse(payload=data, message="User updated")


@users_router.get("/avatars")
async def get_avatars(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_avatars_controller()
    return SuccessResponse(payload=data, message="Avatars retrieved")


@users_router.get("/statistics")
async def get_user_statistics(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_user_statistics_controller(current_user["id"])
    return SuccessResponse(payload=data, message="User statistics retrieved")
