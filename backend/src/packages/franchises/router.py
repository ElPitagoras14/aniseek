from fastapi import APIRouter, Depends

from packages.auth import auth_scheme
from responses import SuccessResponse

from .responses import AnimeFranchiseListOut, FranchiseListOut
from .schemas import FranchiseCreate
from .service import (
    create_franchise_controller,
    get_animes_for_franchises_controller,
    get_franchises_controller,
)

franchises_router = APIRouter()


@franchises_router.get("", response_model=FranchiseListOut)
async def get_franchises(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_franchises_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="Franchises retrieved")


@franchises_router.post("", response_model=SuccessResponse)
async def create_franchise(
    franchise_info: FranchiseCreate,
    current_user: dict = Depends(auth_scheme),
):
    payload = await create_franchise_controller(franchise_info)
    return SuccessResponse(payload=payload, message="Franchise created successfully")


@franchises_router.get("/animes", response_model=AnimeFranchiseListOut)
async def get_animes_for_franchises(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_animes_for_franchises_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="Animes retrieved")
