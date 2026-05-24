from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import auth_settings
from .repository import (
    get_user_by_id,
    get_user_by_username,
)

SECRET_KEY = auth_settings.SECRET_KEY
ALGORITHM = auth_settings.ALGORITHM


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        if not auth_settings.AUTH_ENABLED:
            user = await get_user_by_username(auth_settings.ADMIN_USER)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Admin user not seeded",
                )
            return {
                "id": str(user["id"]),
                "username": user["username"],
                "isActive": user["is_active"],
                "role": user["role_name"],
            }

        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials and credentials.scheme.lower() == "bearer":
            try:
                payload = jwt.decode(
                    credentials.credentials,
                    SECRET_KEY,
                    algorithms=[ALGORITHM],
                )
                user_id = payload.get("id")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token",
                    )

                user = await get_user_by_id(user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found",
                    )

                return {
                    "id": str(user["id"]),
                    "username": user["username"],
                    "isActive": user["is_active"],
                    "role": user["role_name"],
                }

            except JWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No valid Bearer token provided",
        )


auth_scheme = JWTBearer()
