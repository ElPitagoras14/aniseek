import secrets
import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID

from loguru import logger

from database.client import engine
from exceptions import BadRequestError, ForbiddenError, NotFoundError
from packages.auth.utils import hash_invitation_token

from . import repository
from .schemas import InvitationCreateInfo

MAX_EXPIRY_DAYS = 30
INVITABLE_ROLES = ("member", "admin")


def _assert_can_handle(actor: dict, role_name: str) -> None:
    """The owner handles invitations of any role, an admin only 'member' ones."""
    if actor["role"] != "owner" and role_name != "member":
        raise ForbiddenError("Admins can only handle member invitations")


async def create_invitation_controller(actor: dict, info: InvitationCreateInfo) -> dict:
    if info.role not in INVITABLE_ROLES:
        raise BadRequestError("Role must be 'member' or 'admin'")
    _assert_can_handle(actor, info.role)
    if not 1 <= info.expires_in_days <= MAX_EXPIRY_DAYS:
        raise BadRequestError(
            f"Expiration must be between 1 and {MAX_EXPIRY_DAYS} days"
        )

    token = secrets.token_urlsafe(32)
    invitation_id = uuid.uuid4()
    expires_at = datetime.now(timezone.utc) + timedelta(days=info.expires_in_days)
    async with engine.begin() as conn:
        await repository.insert_invitation(
            conn,
            invitation_id,
            hash_invitation_token(token),
            info.role,
            actor["id"],
            expires_at,
        )
    logger.info(
        f"Invitation {invitation_id} ({info.role}) created by {actor['username']}"
    )
    # The only time the token is ever returned.
    return {
        "id": str(invitation_id),
        "token": token,
        "role": info.role,
        "expires_at": expires_at,
    }


async def list_invitations_controller(actor: dict) -> dict:
    role_filter = None if actor["role"] == "owner" else "member"
    async with engine.connect() as conn:
        rows = await repository.list_invitations(conn, role_filter)
    items = [
        {
            "id": str(row["id"]),
            "role": row["role_name"],
            "created_at": row["created_at"],
            "expires_at": row["expires_at"],
            "created_by": row["created_by_username"],
            # Only set once the invitation has been used.
            "used_at": row["used_at"],
            "used_by": row["used_by_username"],
        }
        for row in rows
    ]
    return {"items": items, "total": len(items)}


async def revoke_invitation_controller(actor: dict, invitation_id: UUID) -> None:
    async with engine.connect() as conn:
        invitation = await repository.get_pending_invitation(conn, invitation_id)
    if not invitation:
        raise NotFoundError("Invitation not found")
    _assert_can_handle(actor, invitation["role_name"])
    async with engine.begin() as conn:
        await repository.revoke_invitation(conn, invitation_id)
    logger.info(f"Invitation {invitation_id} revoked by {actor['username']}")
