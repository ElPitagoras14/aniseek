"""Registration policy, invitations and registration itself
(spec: user-registration)."""

import asyncio

import pytest
from factories import auth_headers, create_user


async def _set_policy(raw_conn, policy):
    await raw_conn.execute("UPDATE instance_settings SET registration_policy = $1", policy)


async def _invite(client, creator_id, role="member", **extra):
    response = await client.post(
        "/api/invitations", json={"role": role, **extra}, headers=auth_headers(creator_id)
    )
    return response


async def _register(client, username="newbie", password="secret1", token=None):
    body = {"username": username, "password": password}
    if token:
        body["invitationToken"] = token
    return await client.post("/api/auth/register", json=body)


async def _role_of(raw_conn, username):
    return await raw_conn.fetchval(
        "SELECT r.name FROM users u JOIN role_types r ON r.id = u.role_id "
        "WHERE u.username = $1",
        username,
    )


# --- 5.1 settings -----------------------------------------------------------


async def test_member_cannot_read_or_change_settings(client, raw_conn):
    member = await create_user(raw_conn, role_name="member")

    get = await client.get("/api/settings", headers=auth_headers(member))
    put = await client.put(
        "/api/settings", json={"registrationPolicy": "open"}, headers=auth_headers(member)
    )

    assert get.status_code == 403 and put.status_code == 403
    assert await raw_conn.fetchval("SELECT registration_policy FROM instance_settings") == "invite"


@pytest.mark.parametrize("role", ["admin", "owner"])
async def test_admin_and_owner_change_the_policy_and_it_persists(client, raw_conn, role):
    user = await create_user(raw_conn, role_name=role)

    put = await client.put(
        "/api/settings", json={"registrationPolicy": "open"}, headers=auth_headers(user)
    )
    get = await client.get("/api/settings", headers=auth_headers(user))

    assert put.status_code == 200
    assert get.json()["payload"]["registrationPolicy"] == "open"
    row = await raw_conn.fetchrow(
        "SELECT registration_policy, updated_by FROM instance_settings"
    )
    assert row["registration_policy"] == "open"
    assert str(row["updated_by"]) == user


async def test_invalid_policy_value_is_rejected(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")

    response = await client.put(
        "/api/settings", json={"registrationPolicy": "closed"}, headers=auth_headers(admin)
    )

    assert response.status_code == 422


# --- 5.2 public policy ------------------------------------------------------


async def test_public_policy_returns_only_the_policy(client, raw_conn):
    response = await client.get("/api/auth/registration")

    assert response.status_code == 200
    assert response.json()["payload"] == {"policy": "invite"}


# --- 5.3 invitations --------------------------------------------------------


async def test_owner_creates_an_admin_invitation_and_token_is_stored_hashed(client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")

    response = await _invite(client, owner, "admin")

    assert response.status_code == 200
    payload = response.json()["payload"]
    assert payload["role"] == "admin" and payload["token"]
    stored = await raw_conn.fetchval("SELECT token_hash FROM invitations")
    assert stored != payload["token"]
    assert len(stored) == 64
    days = await raw_conn.fetchval(
        "SELECT extract(epoch FROM expires_at - created_at) / 86400 FROM invitations"
    )
    assert 6.9 < float(days) < 7.1


async def test_admin_cannot_invite_an_admin(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")

    response = await _invite(client, admin, "admin")

    assert response.status_code == 403
    assert await raw_conn.fetchval("SELECT count(*) FROM invitations") == 0


async def test_nobody_can_invite_an_owner(client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")

    assert (await _invite(client, owner, "owner")).status_code == 400
    assert await raw_conn.fetchval("SELECT count(*) FROM invitations") == 0


@pytest.mark.parametrize("days,status", [(30, 200), (1, 200), (31, 400), (0, 400), (-1, 400)])
async def test_invitation_expiry_limits(client, raw_conn, days, status):
    admin = await create_user(raw_conn, role_name="admin")

    response = await _invite(client, admin, expiresInDays=days)

    assert response.status_code == status


async def test_listing_never_exposes_the_token_and_admin_sees_only_members(client, raw_conn):
    owner = await create_user(raw_conn, username="o", role_name="owner")
    admin = await create_user(raw_conn, username="a", role_name="admin")
    member_invite = (await _invite(client, admin)).json()["payload"]
    admin_invite = (await _invite(client, owner, "admin")).json()["payload"]

    as_admin = await client.get("/api/invitations", headers=auth_headers(admin))
    as_owner = await client.get("/api/invitations", headers=auth_headers(owner))

    assert [i["id"] for i in as_admin.json()["payload"]["items"]] == [member_invite["id"]]
    assert {i["id"] for i in as_owner.json()["payload"]["items"]} == {
        member_invite["id"],
        admin_invite["id"],
    }
    for body in (as_admin.text, as_owner.text):
        assert member_invite["token"] not in body and admin_invite["token"] not in body
        assert "token" not in body.lower()


async def test_listing_shows_pending_and_used_but_hides_revoked_and_expired(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    for _ in range(4):
        await _invite(client, admin)
    ids = [r["id"] for r in await raw_conn.fetch("SELECT id FROM invitations ORDER BY created_at")]
    await raw_conn.execute("UPDATE invitations SET used_at = now() WHERE id = $1", ids[0])
    await raw_conn.execute("UPDATE invitations SET revoked_at = now() WHERE id = $1", ids[1])
    await raw_conn.execute(
        "UPDATE invitations SET expires_at = now() - interval '1 day' WHERE id = $1", ids[2]
    )

    response = await client.get("/api/invitations", headers=auth_headers(admin))

    assert {i["id"] for i in response.json()["payload"]["items"]} == {str(ids[0]), str(ids[3])}


async def test_used_invitation_reports_who_used_it_and_pending_ones_do_not(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    used_token = (await _invite(client, admin)).json()["payload"]["token"]
    pending = (await _invite(client, admin)).json()["payload"]
    assert (await _register(client, "the-user", token=used_token)).status_code == 200

    response = await client.get("/api/invitations", headers=auth_headers(admin))

    by_id = {i["id"]: i for i in response.json()["payload"]["items"]}
    used = next(i for i in by_id.values() if i["usedBy"] == "the-user")
    assert used["usedAt"] is not None
    assert by_id[pending["id"]]["usedAt"] is None
    assert by_id[pending["id"]]["usedBy"] is None
    assert used_token not in response.text


async def test_revoke_an_invitation(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    created = (await _invite(client, admin)).json()["payload"]

    revoke = await client.delete(
        f"/api/invitations/{created['id']}", headers=auth_headers(admin)
    )
    register = await _register(client, token=created["token"])

    assert revoke.status_code == 200
    assert register.status_code == 403
    assert await raw_conn.fetchval("SELECT count(*) FROM users") == 1


async def test_admin_cannot_revoke_an_admin_invitation(client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")
    admin = await create_user(raw_conn, role_name="admin")
    created = (await _invite(client, owner, "admin")).json()["payload"]

    response = await client.delete(
        f"/api/invitations/{created['id']}", headers=auth_headers(admin)
    )

    assert response.status_code == 403
    assert await raw_conn.fetchval("SELECT revoked_at FROM invitations") is None


async def test_revoking_unknown_or_used_invitations_is_404(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    created = (await _invite(client, admin)).json()["payload"]
    await raw_conn.execute("UPDATE invitations SET used_at = now()")

    used = await client.delete(f"/api/invitations/{created['id']}", headers=auth_headers(admin))
    unknown = await client.delete(
        "/api/invitations/00000000-0000-0000-0000-000000000009", headers=auth_headers(admin)
    )

    assert used.status_code == 404 and unknown.status_code == 404


# --- 5.4 register -----------------------------------------------------------


async def test_invite_policy_without_a_token_is_403(client, raw_conn):
    response = await _register(client)

    assert response.status_code == 403
    assert await raw_conn.fetchval("SELECT count(*) FROM users") == 0


async def test_open_policy_without_a_token_creates_a_member(client, raw_conn):
    await _set_policy(raw_conn, "open")

    response = await _register(client)

    assert response.status_code == 200
    assert await _role_of(raw_conn, "newbie") == "member"


@pytest.mark.parametrize("policy", ["invite", "open"])
async def test_valid_token_creates_the_role_of_the_invitation(client, raw_conn, policy):
    await _set_policy(raw_conn, policy)
    owner = await create_user(raw_conn, role_name="owner")
    token = (await _invite(client, owner, "admin")).json()["payload"]["token"]

    response = await _register(client, token=token)

    assert response.status_code == 200
    assert await _role_of(raw_conn, "newbie") == "admin"
    row = await raw_conn.fetchrow("SELECT used_at, used_by FROM invitations")
    assert row["used_at"] is not None
    assert await raw_conn.fetchval("SELECT id FROM users WHERE username = 'newbie'") == row["used_by"]


async def test_single_user_mode_rejects_registration_always(client, raw_conn, monkeypatch):
    from packages.auth import auth_settings

    owner = await create_user(raw_conn, role_name="owner")
    token = (await _invite(client, owner)).json()["payload"]["token"]
    await _set_policy(raw_conn, "open")
    monkeypatch.setattr(auth_settings, "AUTH_ENABLED", False)

    with_token = await _register(client, token=token)
    without = await _register(client, username="other")

    assert with_token.status_code == 403 and without.status_code == 403
    assert await raw_conn.fetchval("SELECT count(*) FROM users") == 1
    assert await raw_conn.fetchval("SELECT used_at FROM invitations") is None


async def test_reusing_an_invitation_is_rejected(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    token = (await _invite(client, admin)).json()["payload"]["token"]
    assert (await _register(client, "first", token=token)).status_code == 200

    again = await _register(client, "second", token=token)

    assert again.status_code == 403
    assert await _role_of(raw_conn, "second") is None


async def test_expired_invitation_is_rejected(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    token = (await _invite(client, admin)).json()["payload"]["token"]
    await raw_conn.execute("UPDATE invitations SET expires_at = now() - interval '1 second'")

    assert (await _register(client, token=token)).status_code == 403


async def test_unknown_token_is_rejected_even_with_an_open_policy(client, raw_conn):
    await _set_policy(raw_conn, "open")

    response = await _register(client, token="not-a-real-token")

    assert response.status_code == 403
    assert await raw_conn.fetchval("SELECT count(*) FROM users") == 0


async def test_duplicate_username_is_409_and_does_not_consume_the_invitation(client, raw_conn):
    admin = await create_user(raw_conn, username="taken", role_name="admin")
    token = (await _invite(client, admin)).json()["payload"]["token"]

    response = await _register(client, "taken", token=token)

    assert response.status_code == 409
    assert await raw_conn.fetchval("SELECT used_at FROM invitations") is None
    assert (await _register(client, "free-name", token=token)).status_code == 200


async def test_race_on_the_username_does_not_consume_the_invitation(client, raw_conn, monkeypatch):
    """The username check passes, then another request takes the name: the
    insert fails and the consumed invitation must roll back (design D8)."""
    from packages.auth import repository

    admin = await create_user(raw_conn, role_name="admin")
    token = (await _invite(client, admin)).json()["payload"]["token"]
    real_insert = repository.insert_user

    async def insert_after_name_is_taken(conn, username, *args, **kwargs):
        await raw_conn.execute(
            "INSERT INTO users (id, username, password, role_id) VALUES "
            "(gen_random_uuid(), $1, 'x', (SELECT id FROM role_types WHERE name = 'member'))",
            username,
        )
        return await real_insert(conn, username, *args, **kwargs)

    monkeypatch.setattr(repository, "insert_user", insert_after_name_is_taken)

    response = await _register(client, "contested", token=token)

    assert response.status_code == 409
    assert await raw_conn.fetchval("SELECT used_at FROM invitations") is None


async def test_concurrent_registrations_with_one_token_create_one_user(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    token = (await _invite(client, admin)).json()["payload"]["token"]

    results = await asyncio.gather(
        *[_register(client, f"racer-{i}", token=token) for i in range(5)]
    )

    assert sorted(r.status_code for r in results) == [200, 403, 403, 403, 403]
    assert await raw_conn.fetchval("SELECT count(*) FROM users WHERE username LIKE 'racer-%'") == 1


@pytest.mark.parametrize("password", ["12345", ""])
async def test_short_password_is_rejected(client, raw_conn, password):
    await _set_policy(raw_conn, "open")

    response = await _register(client, password=password)

    assert response.status_code == 400
    assert await raw_conn.fetchval("SELECT count(*) FROM users") == 0
