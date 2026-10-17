import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException
from jose import jwt
from starlette import status

from exceptions import BadRequestError

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
    now = datetime.now(timezone.utc)
    payload = {
        **user_data,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXP_MIN),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_data: dict):
    now = datetime.now(timezone.utc)
    payload = {
        **user_data,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXP_DAY),
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


def build_token_payload(user: dict) -> dict:
    return {
        "id": str(user["id"]),
        "username": user["username"],
        "isActive": user["is_active"],
        "role": user["role_name"],
        "avatarUrl": user["avatar_url"],
        "avatarLabel": user["avatar_label"],
    }


def is_token_stale(payload: dict, credentials_changed_at: datetime | None) -> bool:
    """True if the token predates the user's last credentials change (design D5).

    `iat` has second resolution and `credentials_changed_at` microsecond
    resolution, so the latter is truncated to the second and only a strictly
    older `iat` is rejected: the token issued right after the change, within
    the same second, stays valid."""
    if credentials_changed_at is None:
        return False
    iat = payload.get("iat")
    if iat is None:
        return True
    return iat < int(credentials_changed_at.timestamp())


def hash_secret_token(token: str) -> str:
    """Hash for invitation tokens and API keys. SHA-256 is enough here: both
    are 32 random bytes, not a human-chosen secret, so there is nothing to
    brute-force."""
    return hashlib.sha256(token.encode()).hexdigest()


def validate_credentials(username: str, password: str) -> None:
    """Rules shared by registration, direct creation, password resets and the
    owner bootstrap."""
    if not username or not username.strip():
        raise BadRequestError("Username is required")
    if len(username) > 64:
        raise BadRequestError("Username must be at most 64 characters")
    validate_password(password)


def validate_password(password: str) -> None:
    if not password or len(password) < 6:
        raise BadRequestError("Password must be at least 6 characters")
    # bcrypt only hashes the first 72 bytes and rejects longer input.
    if len(password.encode()) > 72:
        raise BadRequestError("Password must be at most 72 bytes")
