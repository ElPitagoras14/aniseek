from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from starlette import status
from loguru import logger

from databases.postgres import (
    AsyncDatabaseSession,
    Avatar,
    User,
    UserDownloadEpisode,
    UserSaveAnime,
    Anime,
)
from utils.exceptions import ConflictException, NotFoundException
from packages.auth import get_hash, verify_password
from .schemas import UserInfo
from .utils import cast_avatars, cast_statistics, cast_user, cast_users


async def get_users_controller(user_id: str):
    logger.debug("Getting users")
    async with AsyncDatabaseSession() as db:
        stmt = select(User).options(
            selectinload(User.avatar), selectinload(User.role)
        )
        result = await db.execute(stmt)
        users = result.scalars().all()

        specific_user = None
        other_users = []

        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username,
                "avatar_url": user.avatar.url if user.avatar else None,
                "avatar_label": user.avatar.label if user.avatar else None,
                "role": user.role.name,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }

            if user.id == user_id:
                specific_user = user_data
            else:
                other_users.append(user_data)

        all_users = []
        if specific_user:
            all_users.append(specific_user)
        all_users.extend(other_users)

        casted_users = cast_users(all_users, len(all_users))

        return status.HTTP_200_OK, casted_users


async def get_me_controller(user_id: str):
    logger.debug("Getting me")
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.role))
        )
        result = await db.execute(stmt)
        user = result.scalar()
        if not user:
            raise NotFoundException("User not found")
        stmt = select(Avatar).where(Avatar.id == user.avatar_id)
        result = await db.execute(stmt)
        avatar = result.scalar()
        if not avatar:
            raise NotFoundException("Avatar not found")

        user_data = {
            "id": user.id,
            "username": user.username,
            "avatar_url": avatar.url,
            "avatar_label": avatar.label,
            "role": user.role.name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

        casted_user = cast_user(user_data)
        return status.HTTP_200_OK, casted_user


async def check_username_controller(username: str):
    logger.debug(f"Checking username {username}")
    async with AsyncDatabaseSession() as db:
        stmt = select(User).where(User.username == username)
        user = await db.scalar(stmt)
        if user:
            return status.HTTP_200_OK, False
        return status.HTTP_200_OK, True


async def get_avatars_controller():
    logger.debug("Getting avatars")
    async with AsyncDatabaseSession() as db:
        stmt = select(Avatar)
        result = await db.execute(stmt)
        avatars = result.scalars().all()

        avatars = [
            {
                "id": avatar.id,
                "label": avatar.label,
                "url": avatar.url,
            }
            for avatar in avatars
        ]

        casted_avatars = cast_avatars(avatars, len(avatars))

        return status.HTTP_200_OK, casted_avatars


async def update_user_controller(user_info: UserInfo, user_id: str):
    logger.debug(f"Updating user with id: {user_id}")
    async with AsyncDatabaseSession() as db:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar()
        if not user:
            raise NotFoundException("User not found")

        if user_info.username:
            user.username = user_info.username

        if user_info.password:
            if not verify_password(
                user_info.password.current_password, user.password
            ):
                raise ConflictException("Current password is incorrect")
            user.password = get_hash(user_info.password.new_password)

        if user_info.avatar_id:
            user.avatar_id = user_info.avatar_id

        db.add(user)
        return status.HTTP_200_OK, "User updated successfully"


async def get_user_statistics_controller(user_id: str):
    logger.debug("Getting user statistics")
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(func.count())
            .select_from(UserSaveAnime)
            .where(UserSaveAnime.user_id == user_id)
        )
        result_count = await db.execute(stmt)
        saved_animes = result_count.scalar_one()

        stmt = (
            select(func.count())
            .select_from(UserDownloadEpisode)
            .where(UserDownloadEpisode.user_id == user_id)
        )
        result_count = await db.execute(stmt)
        downloaded_episodes = result_count.scalar_one()

        stmt = (
            select(func.count())
            .select_from(UserSaveAnime)
            .join(UserSaveAnime.anime)
            .where(
                UserSaveAnime.user_id == user_id,
                Anime.is_finished.is_(False),
            )
        )
        result_count = await db.execute(stmt)
        in_emission_animes = result_count.scalar_one()

        statistics = {
            "saved_animes": saved_animes,
            "downloaded_episodes": downloaded_episodes,
            "in_emission_animes": in_emission_animes,
        }

        casted_statistics = cast_statistics(statistics)

        return status.HTTP_200_OK, casted_statistics
