from fastapi import APIRouter, Depends

from packages.auth import require_role
from responses import SuccessResponse

from .schemas import OwnerTransferInfo
from .service import transfer_owner_controller

owner_router = APIRouter()


@owner_router.post("/transfer")
async def transfer_owner(
    transfer_info: OwnerTransferInfo,
    current_user: dict = Depends(require_role("owner")),
):
    payload = await transfer_owner_controller(current_user, transfer_info)
    return SuccessResponse(payload=payload, message="Ownership transferred")
