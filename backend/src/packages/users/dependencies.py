from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from packages.auth import auth_scheme
from utils.exceptions import NotFoundException
from databases.postgres import AsyncDatabaseSession, User, Avatar


async def valid_user_id(
    user_id: str,
    current_user: dict = Depends(auth_scheme),
) -> dict:
    """Valida que el usuario existe y retorna los datos."""
    async with AsyncDatabaseSession() as db:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.avatar), selectinload(User.role))
        )
        result = await db.execute(stmt)
        user = result.scalar()

        if not user:
            raise NotFoundException(f"User {user_id} not found")

        return {
            "user_id": user_id,
            "user": user,
        }


async def valid_username(
    username: str,
) -> dict:
    """Valida que el nombre de usuario existe."""
    async with AsyncDatabaseSession() as db:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar()

        if not user:
            raise NotFoundException(f"Username {username} not found")

        return {
            "username": username,
            "user": user,
        }


async def valid_avatar_id(
    avatar_id: int,
) -> dict:
    """Valida que el avatar existe."""
    async with AsyncDatabaseSession() as db:
        stmt = select(Avatar).where(Avatar.id == avatar_id)
        result = await db.execute(stmt)
        avatar = result.scalar()

        if not avatar:
            raise NotFoundException(f"Avatar {avatar_id} not found")

        return {
            "avatar_id": avatar_id,
            "avatar": avatar,
        }
