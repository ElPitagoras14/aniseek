from uuid import UUID

from fastapi import APIRouter, Depends

from packages.auth import auth_scheme, require_role
from responses import SuccessResponse

from .schemas import (
    PasswordResetInfo,
    UserAdminUpdateInfo,
    UserCreateInfo,
    UserUpdateInfo,
)
from .service import (
    check_username_controller,
    create_user_controller,
    get_avatars_controller,
    get_me_controller,
    get_user_statistics_controller,
    get_users_controller,
    reset_user_password_controller,
    update_managed_user_controller,
    update_user_controller,
)

users_router = APIRouter()


@users_router.get("")
async def get_users(
    current_user: dict = Depends(require_role("admin")),
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


@users_router.post("")
async def create_user(
    user_info: UserCreateInfo,
    current_user: dict = Depends(require_role("admin")),
):
    payload = await create_user_controller(current_user, user_info)
    return SuccessResponse(payload=payload, message="User created")


@users_router.patch("/{user_id}")
async def update_managed_user(
    user_id: UUID,
    user_info: UserAdminUpdateInfo,
    current_user: dict = Depends(require_role("admin")),
):
    payload = await update_managed_user_controller(
        current_user, str(user_id), user_info
    )
    return SuccessResponse(payload=payload, message="User updated")


@users_router.put("/{user_id}/password")
async def reset_user_password(
    user_id: UUID,
    password_info: PasswordResetInfo,
    current_user: dict = Depends(require_role("admin")),
):
    payload = await reset_user_password_controller(
        current_user, str(user_id), password_info.password
    )
    return SuccessResponse(payload=payload, message="Password updated")
