from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema para requests de autenticación."""

    username: str
    password: str


class RegisterRequest(BaseModel):
    """Schema para registro de usuarios."""

    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema para refresh de token."""

    refresh_token: str


async def valid_login_request(
    login_info: LoginRequest,
) -> LoginRequest:
    """Valida que los datos de login sean correctos."""
    if not login_info.username or not login_info.password:
        from utils.exceptions import BadRequestException

        raise BadRequestException("Username and password are required")
    return login_info


async def valid_register_request(
    register_info: RegisterRequest,
) -> RegisterRequest:
    """Valida que los datos de registro sean correctos."""
    if not register_info.username or not register_info.password:
        from utils.exceptions import BadRequestException

        raise BadRequestException("Username and password are required")
    if len(register_info.password) < 6:
        from utils.exceptions import BadRequestException

        raise BadRequestException("Password must be at least 6 characters")
    return register_info
