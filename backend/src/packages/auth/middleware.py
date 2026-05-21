from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from . import repository
from .config import auth_settings

SECRET_KEY = auth_settings.SECRET_KEY
ALGORITHM = auth_settings.ALGORITHM


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
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

                user = await repository.get_user_with_role_and_avatar_by_id(user_id)
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
