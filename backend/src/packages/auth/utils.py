from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException
from jose import jwt
from starlette import status

from .config import auth_settings
from .responses import AccessToken, Tokens

SECRET_KEY = auth_settings.SECRET_KEY
ALGORITHM = auth_settings.ALGORITHM
ACCESS_TOKEN_EXP_MIN = auth_settings.ACCESS_TOKEN_EXP_MIN
REFRESH_TOKEN_EXP_DAY = auth_settings.REFRESH_TOKEN_EXP_DAY


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def parse_jwt_data(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None


def create_access_token(user_data: dict):
    payload = {
        **user_data,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXP_MIN),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_data: dict):
    payload = {
        **user_data,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXP_DAY),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_hash(word: str) -> str:
    return bcrypt.hashpw(word.encode(), bcrypt.gensalt()).decode()


def cast_tokens(access_token: str, refresh_token: str):
    return Tokens(access=access_token, refresh=refresh_token)


def cast_access_token(access_token: str):
    return AccessToken(access=access_token)
