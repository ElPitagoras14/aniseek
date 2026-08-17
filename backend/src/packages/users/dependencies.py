from fastapi import Depends

from database.client import engine
from packages.auth import auth_scheme
from exceptions import NotFoundError

from . import repository


async def valid_user_id(
    user_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Validates that the user exists and returns the required data."""
    async with engine.connect() as conn:
        user = await repository.get_user_by_id_with_role_and_avatar(conn, user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found")

    return {
        "user_id": user_id,
        "user": user,
    }


async def valid_username(
    username: str,
) -> dict:
    """Validates that the username exists."""
    async with engine.connect() as conn:
        user = await repository.get_user_by_username(conn, username)
    if not user:
        raise NotFoundError(f"Username {username} not found")

    return {
        "username": username,
        "user": user,
    }


async def valid_avatar_id(
    avatar_id: int,
) -> dict:
    """Validates that the avatar exists."""
    async with engine.connect() as conn:
        avatar = await repository.get_avatar_by_id(conn, avatar_id)
    if not avatar:
        raise NotFoundError(f"Avatar {avatar_id} not found")

    return {
        "avatar_id": avatar_id,
        "avatar": avatar,
    }
