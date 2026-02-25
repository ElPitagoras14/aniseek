from fastapi import APIRouter

from utils.responses import SuccessResponse
from .service import login_controller, refresh_controller, register_controller
from .responses import TokenOut, AccessTokenOut
from .schemas import LoginInfo, CreateInfo

auth_router = APIRouter()


@auth_router.post(
    "/login",
    response_model=TokenOut,
    summary="User login",
    description="Authenticate user and get access token",
)
async def login(login_info: LoginInfo):
    data = await login_controller(login_info.username, login_info.password)
    return SuccessResponse(payload=data, message="User logged in successfully")


@auth_router.post(
    "/register",
    response_model=SuccessResponse,
    summary="User registration",
    description="Register a new user account",
    status_code=201,
)
async def register(register_info: CreateInfo):
    data = await register_controller(
        register_info.username, register_info.password
    )
    return SuccessResponse(
        payload=data, message="User registered successfully"
    )


@auth_router.post(
    "/refresh",
    response_model=AccessTokenOut,
    summary="Refresh access token",
    description="Refresh the access token using a refresh token",
)
async def refresh_token(refresh_token: str):
    _, data = refresh_controller(refresh_token)
    return SuccessResponse(
        payload=data, message="Token refreshed successfully"
    )
