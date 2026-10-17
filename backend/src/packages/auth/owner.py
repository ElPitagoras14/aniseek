from loguru import logger
from sqlalchemy.exc import IntegrityError

from database.client import engine
from exceptions import BadRequestError

from . import repository
from .config import auth_settings
from .utils import get_hash, validate_credentials


class OwnerBootstrapError(RuntimeError):
    """The instance has no owner and one cannot be created. Raised at startup,
    so the API exits instead of running without an owner."""


async def ensure_owner() -> None:
    """Guarantees the instance has an owner (design D3):

    1. an owner already exists: nothing to do, OWNER_* are ignored;
    2. otherwise the oldest active admin is promoted;
    3. otherwise the owner is created from OWNER_USERNAME / OWNER_PASSWORD.
    """
    try:
        async with engine.begin() as conn:
            await _ensure_owner(conn)
    except IntegrityError:
        # Another replica created the owner first (uq_users_single_owner).
        async with engine.connect() as conn:
            if await repository.get_owner_id(conn):
                return
        raise


async def _ensure_owner(conn) -> None:
    if await repository.get_owner_id(conn):
        return

    admin_id = await repository.get_oldest_active_admin_id(conn)
    if admin_id:
        await repository.set_user_role(conn, admin_id, "owner")
        logger.info(f"Promoted existing admin {admin_id} to owner")
        return

    username = auth_settings.OWNER_USERNAME
    password = auth_settings.OWNER_PASSWORD
    # An empty value counts as missing: compose passes `${VAR:-}` as "".
    if not username or not username.strip():
        raise OwnerBootstrapError(
            "The instance has no owner: set OWNER_USERNAME to create one"
        )
    if not password:
        raise OwnerBootstrapError(
            "The instance has no owner: set OWNER_PASSWORD to create one"
        )
    try:
        validate_credentials(username, password)
    except BadRequestError as e:
        variable = "OWNER_PASSWORD" if "assword" in e.message else "OWNER_USERNAME"
        raise OwnerBootstrapError(f"Invalid {variable}: {e.message}") from e

    if await repository.get_user_id_by_username(conn, username):
        raise OwnerBootstrapError(
            f"OWNER_USERNAME '{username}' is already taken by an existing user "
            "and the instance has no owner; choose another username"
        )

    await repository.insert_user(conn, username, get_hash(password), "owner")
    logger.info(f"Created owner '{username}'")
