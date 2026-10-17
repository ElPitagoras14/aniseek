from uuid import UUID

from loguru import logger

from database.client import engine
from exceptions import BadRequestError, ConflictError, NotFoundError
from packages.auth import repository as auth_repository
from packages.auth import verify_password

from .schemas import OwnerTransferInfo


async def transfer_owner_controller(actor: dict, info: OwnerTransferInfo) -> str:
    try:
        target_id = str(UUID(info.target_user_id))
    except ValueError:
        raise BadRequestError("Invalid target user id")
    if target_id == actor["id"]:
        raise BadRequestError("The owner is already the owner")

    async with engine.connect() as conn:
        current = await auth_repository.get_user_by_id(conn, actor["id"])
        target = await auth_repository.get_user_by_id(conn, target_id)
    if not verify_password(info.current_password, current["password"]):
        raise ConflictError("Current password is incorrect")
    if not target:
        raise NotFoundError("Target user not found")
    if not target["is_active"]:
        raise BadRequestError("Target user is not active")

    # One transaction; the current owner is demoted first so the unique index
    # never sees two owners (design D8).
    async with engine.begin() as conn:
        await auth_repository.set_user_role(conn, actor["id"], "admin")
        await auth_repository.set_user_role(conn, target_id, "owner")
    logger.info(
        f"Ownership transferred from {actor['username']} to {target['username']}"
    )
    return "Ownership transferred successfully"
