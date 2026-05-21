from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema for authentication requests."""

    username: str
    password: str


class RegisterRequest(BaseModel):
    """Schema for user registration."""

    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh."""

    refresh_token: str


async def valid_login_request(
    login_info: LoginRequest,
) -> LoginRequest:
    """Validates that login credentials are provided."""
    if not login_info.username or not login_info.password:
        from exceptions import BadRequestError

        raise BadRequestError("Username and password are required")
    return login_info


async def valid_register_request(
    register_info: RegisterRequest,
) -> RegisterRequest:
    """Validates that registration data is correct."""
    if not register_info.username or not register_info.password:
        from exceptions import BadRequestError

        raise BadRequestError("Username and password are required")
    if len(register_info.password) < 6:
        from exceptions import BadRequestError

        raise BadRequestError("Password must be at least 6 characters")
    return register_info
