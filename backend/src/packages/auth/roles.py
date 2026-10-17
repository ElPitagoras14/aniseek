from fastapi import Depends

from exceptions import ForbiddenError

from .middleware import auth_scheme

# Role hierarchy (design D1): permissions live in code as a rank, not in tables.
ROLE_RANK = {"member": 0, "admin": 1, "owner": 2}


def role_rank(role: str | None) -> int:
    return ROLE_RANK.get(role, -1)


def require_role(min_role: str):
    """Dependency factory: 403 unless the request's user has at least `min_role`.

    Use it in the route decorator (`dependencies=[Depends(require_role(...))]`)
    when the check must run before any other dependency that could answer 404."""
    if min_role not in ROLE_RANK:
        raise ValueError(f"Unknown role: {min_role!r}")

    async def dependency(current_user: dict = Depends(auth_scheme)) -> dict:
        if role_rank(current_user["role"]) < ROLE_RANK[min_role]:
            raise ForbiddenError("Insufficient permissions")
        return current_user

    return dependency


def assert_can_manage(actor: dict, target: dict) -> None:
    """Who can act on whose account (user-administration): the owner manages
    admins and members, an admin only members, nobody manages the owner or
    their own account. `actor` has `id` and `role`; `target` has `id` and `role`."""
    if role_rank(actor["role"]) < ROLE_RANK["admin"]:
        raise ForbiddenError("Insufficient permissions")
    if str(actor["id"]) == str(target["id"]):
        raise ForbiddenError("You cannot perform this operation on your own account")
    if target["role"] == "owner":
        raise ForbiddenError("The owner cannot be managed")
    if actor["role"] == "admin" and target["role"] != "member":
        raise ForbiddenError("Admins can only manage members")
