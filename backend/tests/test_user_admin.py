"""What owner and admin can do on other accounts (spec: user-administration)."""

import pytest
from factories import auth_headers, create_user


async def _create(client, actor_id, username="created", role="member", password="secret1"):
    return await client.post(
        "/api/users",
        json={"username": username, "password": password, "role": role},
        headers=auth_headers(actor_id),
    )


async def _patch(client, actor_id, target_id, **body):
    return await client.patch(
        f"/api/users/{target_id}", json=body, headers=auth_headers(actor_id)
    )


async def _role_of(raw_conn, user_id):
    return await raw_conn.fetchval(
        "SELECT r.name FROM users u JOIN role_types r ON r.id = u.role_id "
        "WHERE u.id = $1::uuid",
        user_id,
    )


# --- 6.1 create -------------------------------------------------------------


async def test_admin_creates_a_member_with_the_invite_policy(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")

    response = await _create(client, admin)

    assert response.status_code == 200
    assert response.json()["payload"]["role"] == "member"
    assert response.json()["payload"]["isActive"] is True
    assert await raw_conn.fetchval("SELECT registration_policy FROM instance_settings") == "invite"


async def test_created_user_can_log_in(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    await _create(client, admin, "login-me", password="secret1")

    login = await client.post(
        "/api/auth/login", json={"username": "login-me", "password": "secret1"}
    )

    assert login.status_code == 200


async def test_admin_cannot_create_an_admin_or_an_owner(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")

    as_admin = await _create(client, admin, "x1", role="admin")
    as_owner_role = await _create(client, admin, "x2", role="owner")

    assert as_admin.status_code == 403
    assert as_owner_role.status_code in (400, 403)
    assert await raw_conn.fetchval("SELECT count(*) FROM users") == 1


async def test_owner_creates_an_admin_but_nobody_creates_an_owner(client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")

    admin = await _create(client, owner, "new-admin", role="admin")
    another_owner = await _create(client, owner, "new-owner", role="owner")

    assert admin.status_code == 200 and admin.json()["payload"]["role"] == "admin"
    assert another_owner.status_code == 400
    assert await raw_conn.fetchval("SELECT count(*) FROM users WHERE username = 'new-owner'") == 0


async def test_creation_validates_credentials_and_uniqueness(client, raw_conn):
    admin = await create_user(raw_conn, username="existing", role_name="admin")

    assert (await _create(client, admin, "ok-name", password="123")).status_code == 400
    assert (await _create(client, admin, "  ")).status_code == 400
    assert (await _create(client, admin, "existing")).status_code == 409


# --- 6.2 patch --------------------------------------------------------------


async def test_admin_deactivates_and_reactivates_a_member_keeping_their_data(client, raw_conn):
    from factories import create_anime

    admin = await create_user(raw_conn, role_name="admin")
    member = await create_user(raw_conn, role_name="member", password="secret1")
    anime_id = await create_anime(raw_conn)
    await raw_conn.execute(
        "INSERT INTO user_save_anime (user_id, anime_id) VALUES ($1::uuid, $2)", member, anime_id
    )
    username = await raw_conn.fetchval("SELECT username FROM users WHERE id = $1::uuid", member)

    off = await _patch(client, admin, member, isActive=False)
    token_use = await client.get("/api/users/me", headers=auth_headers(member))
    login = await client.post(
        "/api/auth/login", json={"username": username, "password": "secret1"}
    )

    assert off.status_code == 200 and off.json()["payload"]["isActive"] is False
    assert token_use.status_code == 401
    assert login.status_code == 409
    assert await raw_conn.fetchval("SELECT count(*) FROM user_save_anime") == 1

    on = await _patch(client, admin, member, isActive=True)
    login_again = await client.post(
        "/api/auth/login", json={"username": username, "password": "secret1"}
    )
    assert on.status_code == 200 and login_again.status_code == 200


async def test_admin_cannot_touch_other_admins_or_the_owner(client, raw_conn):
    owner = await create_user(raw_conn, username="o", role_name="owner")
    admin = await create_user(raw_conn, username="a", role_name="admin")
    other_admin = await create_user(raw_conn, username="a2", role_name="admin")

    on_admin = await _patch(client, admin, other_admin, isActive=False)
    on_owner = await _patch(client, admin, owner, isActive=False)

    assert on_admin.status_code == 403 and on_owner.status_code == 403
    assert await raw_conn.fetchval("SELECT count(*) FROM users WHERE is_active") == 3


async def test_nobody_deactivates_or_changes_their_own_account(client, raw_conn):
    owner = await create_user(raw_conn, username="o", role_name="owner")
    admin = await create_user(raw_conn, username="a", role_name="admin")

    assert (await _patch(client, admin, admin, isActive=False)).status_code == 403
    assert (await _patch(client, owner, owner, isActive=False)).status_code == 403
    assert (await _patch(client, owner, owner, role="admin")).status_code == 403
    assert await _role_of(raw_conn, owner) == "owner"
    assert await raw_conn.fetchval("SELECT count(*) FROM users WHERE is_active") == 2


async def test_owner_changes_roles_with_effect_on_the_next_request(client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")
    member = await create_user(raw_conn, role_name="member")
    assert (await client.get("/api/users", headers=auth_headers(member))).status_code == 403

    promote = await _patch(client, owner, member, role="admin")

    assert promote.status_code == 200 and promote.json()["payload"]["role"] == "admin"
    assert (await client.get("/api/users", headers=auth_headers(member))).status_code == 200

    demote = await _patch(client, owner, member, role="member")
    assert demote.status_code == 200
    assert (await client.get("/api/users", headers=auth_headers(member))).status_code == 403


async def test_admin_cannot_change_roles(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    member = await create_user(raw_conn, role_name="member")

    response = await _patch(client, admin, member, role="admin")

    assert response.status_code == 403
    assert await _role_of(raw_conn, member) == "member"


async def test_owner_cannot_assign_owner_by_role_change(client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")
    member = await create_user(raw_conn, role_name="member")

    response = await _patch(client, owner, member, role="owner")

    assert response.status_code == 400
    assert await _role_of(raw_conn, owner) == "owner"
    assert await _role_of(raw_conn, member) == "member"


async def test_patch_of_an_unknown_user_is_404(client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")

    response = await _patch(client, owner, "00000000-0000-0000-0000-000000000009", isActive=False)

    assert response.status_code == 404


async def test_invalid_role_change_leaves_activation_untouched(client, raw_conn):
    """Both fields in one request: a rejected role must not apply is_active."""
    owner = await create_user(raw_conn, role_name="owner")
    member = await create_user(raw_conn, role_name="member")

    response = await _patch(client, owner, member, isActive=False, role="owner")

    assert response.status_code == 400
    assert await raw_conn.fetchval("SELECT is_active FROM users WHERE id = $1::uuid", member)


# --- 6.3 password reset -----------------------------------------------------


async def test_admin_resets_a_members_password_and_old_sessions_die(client, raw_conn):
    from packages.auth.utils import create_access_token, create_refresh_token

    admin = await create_user(raw_conn, role_name="admin")
    member = await create_user(raw_conn, role_name="member", password="old-pass1")
    username = await raw_conn.fetchval("SELECT username FROM users WHERE id = $1::uuid", member)
    old_access = create_access_token({"id": member})
    old_refresh = create_refresh_token({"id": member})
    # Tokens carry second-resolution iat: make the reset land in a later second.
    await raw_conn.execute("SELECT pg_sleep(1.1)")

    response = await client.put(
        f"/api/users/{member}/password",
        json={"password": "new-pass1"},
        headers=auth_headers(admin),
    )

    assert response.status_code == 200
    new = await client.post("/api/auth/login", json={"username": username, "password": "new-pass1"})
    old = await client.post("/api/auth/login", json={"username": username, "password": "old-pass1"})
    assert new.status_code == 200
    assert old.status_code == 409
    me = await client.get("/api/users/me", headers={"Authorization": f"Bearer {old_access}"})
    refresh = await client.post("/api/auth/refresh", params={"refresh_token": old_refresh})
    assert me.status_code == 401 and refresh.status_code == 401
    new_token = new.json()["payload"]["access"]
    assert (
        await client.get("/api/users/me", headers={"Authorization": f"Bearer {new_token}"})
    ).status_code == 200


async def test_admin_cannot_reset_the_owner_or_another_admin(client, raw_conn):
    owner = await create_user(raw_conn, username="o", role_name="owner", password="owner-pass")
    admin = await create_user(raw_conn, username="a", role_name="admin")
    other = await create_user(raw_conn, username="a2", role_name="admin", password="other-pass")
    before = await raw_conn.fetch("SELECT password FROM users ORDER BY username")

    for target in (owner, other, admin):
        response = await client.put(
            f"/api/users/{target}/password",
            json={"password": "hijacked1"},
            headers=auth_headers(admin),
        )
        assert response.status_code == 403

    assert await raw_conn.fetch("SELECT password FROM users ORDER BY username") == before


async def test_password_reset_validates_the_new_password(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    member = await create_user(raw_conn, role_name="member")

    response = await client.put(
        f"/api/users/{member}/password", json={"password": "123"}, headers=auth_headers(admin)
    )

    assert response.status_code == 400


@pytest.mark.parametrize("new_password", ["123", "x" * 80])
async def test_own_password_change_validates_the_new_password(client, raw_conn, new_password):
    member = await create_user(raw_conn, password="secret1")

    response = await client.put(
        "/api/users",
        json={"password": {"currentPassword": "secret1", "newPassword": new_password}},
        headers=auth_headers(member),
    )

    assert response.status_code == 400
