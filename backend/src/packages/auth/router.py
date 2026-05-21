from fastapi import APIRouter

from responses import SuccessResponse

from .responses import AccessTokenOut, TokenOut
from .schemas import LoginInfo, RegisterInfo
from .service import login_controller, refresh_controller, register_controller

auth_router = APIRouter()


@auth_router.post("/login", response_model=TokenOut)
async def login(login_info: LoginInfo):
    payload = await login_controller(login_info.username, login_info.password)
    return SuccessResponse(payload=payload, message="User logged in successfully")


@auth_router.post("/register", response_model=SuccessResponse)
async def register(register_info: RegisterInfo):
    payload = await register_controller(register_info.username, register_info.password)
    return SuccessResponse(payload=payload, message="User registered successfully")


@auth_router.post("/refresh", response_model=AccessTokenOut)
async def refresh_token(refresh_token: str):
    payload = refresh_controller(refresh_token)
    return SuccessResponse(payload=payload, message="Token refreshed successfully")
