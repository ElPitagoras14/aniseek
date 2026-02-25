from fastapi import APIRouter, Depends

from utils.responses import SuccessResponse
from packages.auth import auth_scheme
from .service import (
    create_franchise_controller,
    get_animes_for_franchises_controller,
    get_franchises_controller,
)
from .responses import (
    AnimeFranchiseListOut,
    FranchiseListOut,
)
from .schemas import CreateFranchise

franchises_router = APIRouter()


@franchises_router.get(
    "",
    response_model=FranchiseListOut,
    summary="Get all franchises",
    description="Retrieve all anime franchises",
)
async def get_franchises(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_franchises_controller(current_user["id"])
    return SuccessResponse(payload=data, message="Franchises retrieved")


@franchises_router.post(
    "",
    response_model=SuccessResponse,
    summary="Create franchise",
    description="Create a new anime franchise",
    status_code=201,
)
async def create_franchise(
    franchise_info: CreateFranchise,
    current_user: dict = Depends(auth_scheme),
):
    data = await create_franchise_controller(franchise_info)
    return SuccessResponse(
        payload=data, message="Franchise created successfully"
    )


@franchises_router.get(
    "/animes",
    response_model=AnimeFranchiseListOut,
    summary="Get animes for franchises",
    description="Get animes that can be added to franchises",
)
async def get_animes_for_franchises(
    current_user: dict = Depends(auth_scheme),
):
    data = await get_animes_for_franchises_controller(current_user["id"])
    return SuccessResponse(payload=data, message="Animes retrieved")
