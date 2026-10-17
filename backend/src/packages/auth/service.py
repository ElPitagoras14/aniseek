from loguru import logger
from sqlalchemy.exc import IntegrityError

from database.client import engine
from exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)

from . import repository
from .config import auth_settings
from .utils import (
    build_token_payload,
    cast_access_token,
    cast_tokens,
    create_access_token,
    create_refresh_token,
    get_hash,
    hash_invitation_token,
    is_token_stale,
    validate_credentials,
    verify_password,
    verify_token,
)


async def login_controller(username: str, password: str):
    logger.debug(f"User {username} is trying to log in")
    async with engine.connect() as conn:
        user = await repository.get_user_by_username(conn, username)
    if not user:
        logger.debug(f"User {username} not found")
        raise NotFoundError("User not found")
    if not verify_password(password, user["password"]):
        logger.debug(f"Password for user {username} is wrong")
        raise ConflictError("Password is wrong")
    if not user["is_active"]:
        logger.debug(f"User {username} is not active")
        raise ConflictError("User is not active")
    logger.info(f"User {username} logged in")
    token_payload = build_token_payload(user)
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)
    return cast_tokens(access_token, refresh_token)


async def get_registration_policy_controller() -> dict:
    async with engine.connect() as conn:
        policy = await repository.get_registration_policy(conn)
    return {"policy": policy}


async def register_controller(
    username: str, password: str, invitation_token: str | None = None
):
    logger.debug(f"User {username} is trying to register")
    if not auth_settings.AUTH_ENABLED:
        raise ForbiddenError("Registration is disabled in single-user mode")

    if not invitation_token:
        async with engine.connect() as conn:
            policy = await repository.get_registration_policy(conn)
        if policy != "open":
            raise ForbiddenError("Registration requires an invitation")

    validate_credentials(username, password)
    async with engine.connect() as conn:
        existing_id = await repository.get_user_id_by_username(conn, username)
    if existing_id:
        logger.debug(f"User {username} already exists")
        raise ConflictError("User already exists")

    hashed_password = get_hash(password)
    try:
        # One transaction: the invitation is only consumed if the user is
        # created (design D8).
        async with engine.begin() as conn:
            role_name = "member"
            invitation = None
            if invitation_token:
                invitation = await repository.consume_invitation(
                    conn, hash_invitation_token(invitation_token)
                )
                if not invitation:
                    raise ForbiddenError("Invitation is invalid, expired or already used")
                role_name = invitation["role_name"]
            user_id = await repository.insert_user(
                conn, username, hashed_password, role_name
            )
            if invitation:
                await repository.set_invitation_used_by(conn, invitation["id"], user_id)
    except IntegrityError:
        # Lost a race on the username after the check above.
        raise ConflictError("User already exists")
    logger.info(f"User {username} registered as {role_name}")
    return "User registered successfully"


async def refresh_controller(refresh_token: str):
    logger.info("Refreshing access token")
    if not refresh_token:
        logger.warning("Refresh token missing in request")
        raise ConflictError("No refresh token provided")
    payload = verify_token(refresh_token)
    if not payload:
        logger.warning("Invalid refresh token provided")
        raise ConflictError("Invalid refresh token")

    user_id = payload.get("id")
    async with engine.connect() as conn:
        user = await repository.get_user_by_id(conn, user_id) if user_id else None
    if not user or not user["is_active"]:
        logger.warning("Refresh rejected: user missing or inactive")
        raise UnauthorizedError("User not found or not active")
    if is_token_stale(payload, user["credentials_changed_at"]):
        logger.warning("Refresh rejected: credentials changed since token issue")
        raise UnauthorizedError("Token no longer valid")

    # Rebuilt from the database so the new token carries the current role.
    new_access_token = create_access_token(build_token_payload(user))
    casted_access_token = cast_access_token(new_access_token)
    logger.info(f"Access token refreshed successfully for user: {user['username']}")
    return casted_access_token
