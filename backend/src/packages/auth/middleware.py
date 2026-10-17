from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from database.client import engine
from .config import auth_settings
from .repository import (
    get_owner_user,
    get_user_by_id,
)
from .utils import is_token_stale

SECRET_KEY = auth_settings.SECRET_KEY
ALGORITHM = auth_settings.ALGORITHM


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _current_user(user: dict) -> dict:
    return {
        "id": str(user["id"]),
        "username": user["username"],
        "isActive": user["is_active"],
        "role": user["role_name"],
    }


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        if not auth_settings.AUTH_ENABLED:
            # Single-user mode: every request is the instance owner, whatever
            # its username is (access-control, design D6).
            async with engine.connect() as conn:
                user = await get_owner_user(conn)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Instance owner not found",
                )
            return _current_user(user)

        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials and credentials.scheme.lower() == "bearer":
            try:
                payload = jwt.decode(
                    credentials.credentials,
                    SECRET_KEY,
                    algorithms=[ALGORITHM],
                )
            except JWTError:
                raise _unauthorized("Invalid token")

            user_id = payload.get("id")
            if not user_id:
                raise _unauthorized("Invalid token")

            async with engine.connect() as conn:
                user = await get_user_by_id(conn, user_id)
            if not user:
                raise _unauthorized("User not found")
            if not user["is_active"]:
                raise _unauthorized("User is not active")
            if is_token_stale(payload, user["credentials_changed_at"]):
                raise _unauthorized("Token no longer valid")

            return _current_user(user)

        raise _unauthorized("No valid Bearer token provided")


auth_scheme = JWTBearer()
