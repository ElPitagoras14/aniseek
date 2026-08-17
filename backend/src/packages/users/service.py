from loguru import logger

from database.client import engine
from packages.auth import get_hash, verify_password
from exceptions import ConflictError, NotFoundError

from . import repository
from .schemas import UserUpdateInfo
from .utils import cast_avatars, cast_statistics, cast_user, cast_users


def _build_user_data(row: dict) -> dict:
    return {
        "id": row["id"],
        "username": row["username"],
        "avatar_url": row.get("avatar_url"),
        "avatar_label": row.get("avatar_label"),
        "role": row["role_name"],
        "is_active": row["is_active"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


async def get_users_controller(user_id: str):
    logger.debug("Getting users")
    async with engine.connect() as conn:
        users = await repository.list_users_with_role_and_avatar(conn)

    specific_user = None
    other_users = []
    for user in users:
        user_data = _build_user_data(user)
        if str(user["id"]) == user_id:
            specific_user = user_data
        else:
            other_users.append(user_data)

    all_users = []
    if specific_user:
        all_users.append(specific_user)
    all_users.extend(other_users)

    return cast_users(all_users, len(all_users))


async def get_me_controller(user_id: str):
    logger.debug("Getting me")
    async with engine.connect() as conn:
        user = await repository.get_user_with_role(conn, user_id)
        if not user:
            raise NotFoundError("User not found")
        avatar = (
            await repository.get_avatar_by_id(conn, user["avatar_id"])
            if user["avatar_id"]
            else None
        )
    if not avatar:
        raise NotFoundError("Avatar not found")

    user_data = {
        "id": user["id"],
        "username": user["username"],
        "avatar_url": avatar["url"],
        "avatar_label": avatar["label"],
        "role": user["role_name"],
        "is_active": user["is_active"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }
    return cast_user(user_data)


async def check_username_controller(username: str):
    logger.debug(f"Checking username {username}")
    async with engine.connect() as conn:
        exists = await repository.username_exists(conn, username)
    return not exists


async def get_avatars_controller():
    logger.debug("Getting avatars")
    async with engine.connect() as conn:
        avatars = await repository.list_avatars(conn)
    return cast_avatars(avatars, len(avatars))


async def update_user_controller(user_info: UserUpdateInfo, user_id: str):
    logger.debug(f"Updating user with id: {user_id}")
    async with engine.connect() as conn:
        user = await repository.get_user_with_role(conn, user_id)
    if not user:
        raise NotFoundError("User not found")

    if user_info.username:
        async with engine.begin() as conn:
            await repository.update_user_username(conn, user_id, user_info.username)

    if user_info.password:
        async with engine.connect() as conn:
            current_hashed = await repository.get_user_current_password(conn, user_id)
        if not verify_password(user_info.password.current_password, current_hashed):
            raise ConflictError("Current password is incorrect")
        async with engine.begin() as conn:
            await repository.update_user_password(
                conn, user_id, get_hash(user_info.password.new_password)
            )

    if user_info.avatar_id:
        async with engine.begin() as conn:
            await repository.update_user_avatar(conn, user_id, user_info.avatar_id)

    return "User updated successfully"


async def get_user_statistics_controller(user_id: str):
    logger.debug("Getting user statistics")
    async with engine.connect() as conn:
        statistics = {
            "saved_animes": await repository.count_saved_animes(conn, user_id),
            "downloaded_episodes": await repository.count_downloaded_episodes(
                conn, user_id
            ),
            "in_emission_animes": await repository.count_in_emission_saved_animes(
                conn, user_id
            ),
        }
    return cast_statistics(statistics)
