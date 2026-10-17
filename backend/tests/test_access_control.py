"""Role hierarchy, per-endpoint role enforcement and session validity
(specs: access-control, user-administration limits)."""

import itertools

import pytest
from factories import auth_headers, create_anime, create_episode, create_user

ROLES = ["member", "admin", "owner"]


# --- 2.2 / 2.3: rank and management rules (unit) ---------------------------


def test_role_rank_orders_member_admin_owner():
    from packages.auth import role_rank

    assert role_rank("member") < role_rank("admin") < role_rank("owner")
    assert role_rank("guest") < role_rank("member")
    assert role_rank(None) < role_rank("member")


def test_require_role_rejects_unknown_minimum_role():
    from packages.auth import require_role

    with pytest.raises(ValueError):
        require_role("guest")


@pytest.mark.parametrize(
    "actor_role,target_role,allowed",
    [
        ("member", "member", False),
        ("member", "admin", False),
        ("member", "owner", False),
        ("admin", "member", True),
        ("admin", "admin", False),
        ("admin", "owner", False),
        ("owner", "member", True),
        ("owner", "admin", True),
        ("owner", "owner", False),
    ],
)
def test_assert_can_manage_matrix(actor_role, target_role, allowed):
    from exceptions import ForbiddenError
    from packages.auth import assert_can_manage

    actor = {"id": "a", "role": actor_role}
    target = {"id": "b", "role": target_role}
    if allowed:
        assert_can_manage(actor, target)
    else:
        with pytest.raises(ForbiddenError):
            assert_can_manage(actor, target)


@pytest.mark.parametrize("role", ROLES)
def test_assert_can_manage_never_applies_to_oneself(role):
    from exceptions import ForbiddenError
    from packages.auth import assert_can_manage

    me = {"id": "same", "role": role}
    with pytest.raises(ForbiddenError):
        assert_can_manage(me, me)


# --- 2.4 / 2.5: per-endpoint enforcement over HTTP -------------------------


async def _users(raw_conn):
    return {role: await create_user(raw_conn, role_name=role) for role in ROLES}


async def test_member_cannot_delete_storage_and_nothing_changes(client, raw_conn):
    anime_id = await create_anime(raw_conn)
    await create_episode(raw_conn, anime_id=anime_id, size=1234, job_id="job-1")
    member = await create_user(raw_conn, role_name="member")

    response = await client.delete(
        f"/api/episodes/storage/{anime_id}", headers=auth_headers(member)
    )

    assert response.status_code == 403, response.text
    row = await raw_conn.fetchrow("SELECT size, job_id FROM episodes")
    assert (row["size"], row["job_id"]) == (1234, "job-1")


@pytest.mark.parametrize("role", ["admin", "owner"])
async def test_admin_and_owner_can_delete_storage(client, raw_conn, role):
    anime_id = await create_anime(raw_conn)
    await create_episode(raw_conn, anime_id=anime_id, size=1234, job_id="job-1")
    user = await create_user(raw_conn, role_name=role)

    response = await client.delete(
        f"/api/episodes/storage/{anime_id}", headers=auth_headers(user)
    )

    assert response.status_code == 200
    assert (await raw_conn.fetchval("SELECT size FROM episodes")) is None


async def test_member_cannot_create_a_franchise_and_nothing_changes(
    client, raw_conn, mock_dramatiq
):
    anime_id = await create_anime(raw_conn, franchise_id=None)
    member = await create_user(raw_conn, role_name="member")

    response = await client.post(
        "/api/franchises",
        json={"franchise": "Nope", "animes": [{"id": anime_id, "season": 1}]},
        headers=auth_headers(member),
    )

    assert response.status_code == 403
    assert await raw_conn.fetchval("SELECT count(*) FROM franchises") == 0
    mock_dramatiq["order_franchise"].assert_not_called()


@pytest.mark.parametrize("role", ["admin", "owner"])
async def test_admin_and_owner_can_create_a_franchise(
    client, raw_conn, mock_dramatiq, role
):
    anime_id = await create_anime(raw_conn, franchise_id=None)
    user = await create_user(raw_conn, role_name=role)

    response = await client.post(
        "/api/franchises",
        json={"franchise": "Yes", "animes": [{"id": anime_id, "season": 1}]},
        headers=auth_headers(user),
    )

    assert response.status_code == 200
    assert await raw_conn.fetchval("SELECT count(*) FROM franchises") == 1


async def test_user_listing_has_no_password_data(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    await create_user(raw_conn, role_name="owner")

    response = await client.get("/api/users", headers=auth_headers(admin))

    assert response.status_code == 200
    body = response.text
    assert "password" not in body.lower()
    assert "not-a-real-hash" not in body
    assert response.json()["payload"]["total"] == 2


# (method, path, json body, minimum role). A fresh UUID stands in for ids: the
# role check must answer 403 before anything looks the resource up.
_UNKNOWN = "00000000-0000-0000-0000-000000000001"
MATRIX = [
    ("GET", "/api/users/me", None, "member"),
    ("GET", "/api/users/statistics", None, "member"),
    ("GET", "/api/franchises", None, "member"),
    ("GET", "/api/users", None, "admin"),
    ("POST", "/api/users", {"username": "matrix-u", "password": "secret1"}, "admin"),
    ("PATCH", f"/api/users/{_UNKNOWN}", {"isActive": False}, "admin"),
    ("PUT", f"/api/users/{_UNKNOWN}/password", {"password": "secret1"}, "admin"),
    ("GET", "/api/invitations", None, "admin"),
    ("POST", "/api/invitations", {}, "admin"),
    ("DELETE", f"/api/invitations/{_UNKNOWN}", None, "admin"),
    ("GET", "/api/settings", None, "admin"),
    ("PUT", "/api/settings", {"registrationPolicy": "invite"}, "admin"),
    ("DELETE", "/api/episodes/storage/no-such-anime", None, "admin"),
    ("POST", "/api/franchises", {"franchise": "X", "animes": []}, "admin"),
    (
        "POST",
        "/api/owner/transfer",
        {"targetUserId": _UNKNOWN, "currentPassword": "x"},
        "owner",
    ),
]


@pytest.mark.parametrize(
    "method,path,body,min_role,role",
    [(*row, role) for row, role in itertools.product(MATRIX, ROLES)],
)
async def test_permission_matrix(
    client, raw_conn, mock_dramatiq, method, path, body, min_role, role
):
    user = await create_user(raw_conn, role_name=role, password="secret1")

    response = await client.request(
        method, path, json=body, headers=auth_headers(user)
    )

    if ROLES.index(role) < ROLES.index(min_role):
        assert response.status_code == 403
    else:
        # Allowed: whatever the endpoint answers (404, 400, 409, 200...), it is
        # neither an authentication nor an authorization failure.
        assert response.status_code not in (401, 403)


async def test_request_without_token_is_401(client):
    assert (await client.get("/api/users/me")).status_code == 401


async def test_role_change_takes_effect_on_the_next_request(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    headers = auth_headers(admin)
    assert (await client.get("/api/users", headers=headers)).status_code == 200

    await raw_conn.execute(
        "UPDATE users SET role_id = (SELECT id FROM role_types WHERE name = 'member')"
    )

    assert (await client.get("/api/users", headers=headers)).status_code == 403


async def test_token_of_a_deleted_user_is_401(client, raw_conn):
    user = await create_user(raw_conn)
    headers = auth_headers(user)
    await raw_conn.execute("DELETE FROM users")

    assert (await client.get("/api/users/me", headers=headers)).status_code == 401


# --- 3: sessions ------------------------------------------------------------


async def test_token_of_an_inactive_user_is_401(client, raw_conn):
    user = await create_user(raw_conn)
    headers = auth_headers(user)
    assert (await client.get("/api/users/me", headers=headers)).status_code == 200

    await raw_conn.execute("UPDATE users SET is_active = FALSE")

    assert (await client.get("/api/users/me", headers=headers)).status_code == 401


async def test_refresh_is_rejected_for_inactive_and_missing_users(client, raw_conn):
    from packages.auth.utils import create_refresh_token

    user = await create_user(raw_conn)
    refresh = create_refresh_token({"id": user})
    ok = await client.post("/api/auth/refresh", params={"refresh_token": refresh})
    assert ok.status_code == 200

    await raw_conn.execute("UPDATE users SET is_active = FALSE")
    inactive = await client.post("/api/auth/refresh", params={"refresh_token": refresh})
    assert inactive.status_code == 401

    await raw_conn.execute("DELETE FROM users")
    missing = await client.post("/api/auth/refresh", params={"refresh_token": refresh})
    assert missing.status_code == 401


async def test_refreshed_token_carries_the_current_role(client, raw_conn):
    from jose import jwt
    from packages.auth.utils import create_refresh_token

    user = await create_user(raw_conn, role_name="admin")
    refresh = create_refresh_token({"id": user, "role": "member"})

    response = await client.post("/api/auth/refresh", params={"refresh_token": refresh})

    access = response.json()["payload"]["access"]
    assert jwt.get_unverified_claims(access)["role"] == "admin"


async def test_token_issued_before_a_password_change_is_rejected(client, raw_conn):
    from packages.auth.utils import create_access_token, create_refresh_token

    user = await create_user(raw_conn, password="secret1")
    old_access = create_access_token({"id": user})
    old_refresh = create_refresh_token({"id": user})
    # Credentials changed in the future of the token's second.
    await raw_conn.execute(
        "UPDATE users SET credentials_changed_at = now() + interval '5 seconds'"
    )

    me = await client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {old_access}"}
    )
    refresh = await client.post(
        "/api/auth/refresh", params={"refresh_token": old_refresh}
    )

    assert me.status_code == 401
    assert refresh.status_code == 401


async def test_login_right_after_a_password_change_is_accepted(client, raw_conn):
    """Same-second login after PUT /users must not be rejected (design D5)."""
    user = await create_user(raw_conn, password="secret1")
    username = await raw_conn.fetchval("SELECT username FROM users")

    change = await client.put(
        "/api/users",
        json={"password": {"currentPassword": "secret1", "newPassword": "secret2"}},
        headers=auth_headers(user),
    )
    assert change.status_code == 200
    assert (
        await raw_conn.fetchval("SELECT credentials_changed_at FROM users")
    ) is not None

    login = await client.post(
        "/api/auth/login", json={"username": username, "password": "secret2"}
    )
    assert login.status_code == 200
    token = login.json()["payload"]["access"]
    me = await client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200

    # And the token from before the change no longer works once its second is
    # strictly older than the change.
    await raw_conn.execute(
        "UPDATE users SET credentials_changed_at = now() + interval '5 seconds'"
    )
    assert (
        await client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    ).status_code == 401
