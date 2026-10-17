from uuid import UUID

from fastapi import APIRouter, Depends

from packages.auth import require_role
from responses import SuccessResponse

from .schemas import InvitationCreateInfo
from .service import (
    create_invitation_controller,
    list_invitations_controller,
    revoke_invitation_controller,
)

invitations_router = APIRouter()


@invitations_router.get("")
async def list_invitations(
    current_user: dict = Depends(require_role("admin")),
):
    payload = await list_invitations_controller(current_user)
    return SuccessResponse(payload=payload, message="Invitations retrieved")


@invitations_router.post("")
async def create_invitation(
    invitation_info: InvitationCreateInfo,
    current_user: dict = Depends(require_role("admin")),
):
    payload = await create_invitation_controller(current_user, invitation_info)
    return SuccessResponse(payload=payload, message="Invitation created")


@invitations_router.delete("/{invitation_id}")
async def revoke_invitation(
    invitation_id: UUID,
    current_user: dict = Depends(require_role("admin")),
):
    await revoke_invitation_controller(current_user, invitation_id)
    return SuccessResponse(payload=None, message="Invitation revoked")
