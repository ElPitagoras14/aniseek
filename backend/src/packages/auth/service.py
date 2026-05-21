from loguru import logger

from utils.exceptions import ConflictException, NotFoundException

from . import repository
from .utils import (
    cast_access_token,
    cast_tokens,
    create_access_token,
    create_refresh_token,
    get_hash,
    verify_password,
    verify_token,
)


async def login_controller(username: str, password: str):
    logger.debug(f"User {username} is trying to log in")
    user = await repository.get_user_with_role_and_avatar_by_username(username)
    if not user:
        logger.debug(f"User {username} not found")
        raise NotFoundException("User not found")
    if not verify_password(password, user["password"]):
        logger.debug(f"Password for user {username} is wrong")
        raise ConflictException("Password is wrong")
    if not user["is_active"]:
        logger.debug(f"User {username} is not active")
        raise ConflictException("User is not active")
    logger.info(f"User {username} logged in")
    token_payload = {
        "id": str(user["id"]),
        "username": user["username"],
        "isActive": user["is_active"],
        "role": user["role_name"],
        "avatarUrl": user["avatar_url"],
        "avatarLabel": user["avatar_label"],
    }
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)
    return cast_tokens(access_token, refresh_token)


async def register_controller(username: str, password: str):
    logger.debug(f"User {username} is trying to register")
    existing_id = await repository.get_user_id_by_username(username)
    if existing_id:
        logger.debug(f"User {username} already exists")
        raise ConflictException("User already exists")
    hashed_password = get_hash(password)
    await repository.insert_user(username, hashed_password)
    logger.info(f"User {username} registered")
    return "User registered successfully"


def refresh_controller(refresh_token: str):
    logger.info("Refreshing access token")
    if not refresh_token:
        logger.warning("Refresh token missing in request")
        raise ConflictException("No refresh token provided")
    payload = verify_token(refresh_token)
    if not payload:
        logger.warning("Invalid refresh token provided")
        raise ConflictException("Invalid refresh token")
    new_access_token = create_access_token(payload)
    casted_access_token = cast_access_token(new_access_token)
    logger.info(
        f"Access token refreshed successfully for user: {payload.get('username')}"
    )
    return casted_access_token
