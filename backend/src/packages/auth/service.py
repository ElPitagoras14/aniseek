from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette import status

from databases.postgres import AsyncDatabaseSession, User
from utils.exceptions import NotFoundException, ConflictException
from .utils import (
    get_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    cast_tokens,
    cast_access_token,
)


async def login_controller(username: str, password: str):
    logger.debug(f"User {username} is trying to log in")
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(User)
            .where(User.username == username)
            .options(selectinload(User.role), selectinload(User.avatar))
        )
        user = await db.scalar(stmt)
        if not user:
            logger.debug(f"User {username} not found")
            raise NotFoundException("User not found")
        if not verify_password(password, user.password):
            logger.debug(f"Password for user {username} is wrong")
            raise ConflictException("Password is wrong")
        if not user.is_active:
            logger.debug(f"User {username} is not active")
            raise ConflictException("User is not active")
        logger.info(f"User {username} logged in")
        access_token = create_access_token(
            {
                "id": str(user.id),
                "username": user.username,
                "isActive": user.is_active,
                "role": user.role.name,
                "avatarUrl": user.avatar.url if user.avatar else None,
                "avatarLabel": user.avatar.label if user.avatar else None,
            },
        )
        refresh_token = create_refresh_token(
            {
                "id": str(user.id),
                "username": user.username,
                "isActive": user.is_active,
                "role": user.role.name,
                "avatarUrl": user.avatar.url if user.avatar else None,
                "avatarLabel": user.avatar.label if user.avatar else None,
            },
        )
        casted_tokens = cast_tokens(access_token, refresh_token)
        return casted_tokens


async def register_controller(username: str, password: str):
    logger.debug(f"User {username} is trying to register")
    async with AsyncDatabaseSession() as db:
        stmt = select(User).where(User.username == username)
        user = await db.scalar(stmt)
        if user:
            logger.debug(f"User {username} already exists")
            raise ConflictException("User already exists")
        hashed_password = get_hash(password)
        user = User(username=username, password=hashed_password)
        db.add(user)
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
    logger.info(f"Access token refreshed successfully for user: {payload.get('username')}")
    return casted_access_token
