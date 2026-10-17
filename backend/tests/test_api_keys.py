"""API key lifecycle, owner management and authentication by key
(specs: api-keys, access-control)."""

import httpx
import pytest
from factories import auth_headers, create_user


async def _generate(client, user_id: str) -> dict:
    response = await client.post("/api/api-keys/me", headers=auth_headers(user_id))
    assert response.status_code == 200, response.text
    return response.json()["payload"]


@pytest.fixture
async def key_client():
    """A minimal app whose routes declare authentication by API key, since no
    production route accepts one yet (the MCP arrives in `mcp-server`)."""
    from fastapi import Depends, FastAPI

    from exceptions import AppError
    from handlers import app_error_handler
    from packages.auth import api_key_scheme, assert_min_role

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)

    @app.get("/whoami")
    async def whoami(current_user: dict = Depends(api_key_scheme)):
        return current_user

    @app.get("/admin-only")
    async def admin_only(current_user: dict = Depends(api_key_scheme)):
        assert_min_role(current_user, "admin")
        return current_user

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def _bearer(key: str) -> dict:
    return {"Authorization": f"Bearer {key}"}


# --- 4.1: lifecycle ----------------------------------------------------------


async def test_user_without_key(client, raw_conn):
    member = await create_user(raw_conn)

    response = await client.get("/api/api-keys/me", headers=auth_headers(member))

    assert response.status_code == 200, response.text
    assert response.json()["payload"] is None


async def test_generate_returns_full_key_once(client, raw_conn):
    member = await create_user(raw_conn)

    created = await _generate(client, member)
    fetched = (
        await client.get("/api/api-keys/me", headers=auth_headers(member))
    ).json()["payload"]

    assert created["key"].startswith("ask_")
    assert created["key"].startswith(created["prefix"])
    assert len(created["prefix"]) == 12
    assert fetched["prefix"] == created["prefix"]
    assert fetched["lastUsedAt"] is None
    assert "key" not in fetched
    assert created["key"] not in str(fetched)


async def test_full_key_is_not_stored(client, raw_conn):
    member = await create_user(raw_conn)

    key = (await _generate(client, member))["key"]

    row = await raw_conn.fetchrow("SELECT * FROM api_keys")
    assert all(key not in str(value) for value in row.values())


async def test_regenerate_replaces_the_key(client, key_client, raw_conn):
    member = await create_user(raw_conn)
    old = (await _generate(client, member))["key"]

    new = (await _generate(client, member))["key"]

    assert new != old
    assert (await key_client.get("/whoami", headers=_bearer(old))).status_code == 401
    assert (await key_client.get("/whoami", headers=_bearer(new))).status_code == 200
    assert await raw_conn.fetchval("SELECT count(*) FROM api_keys") == 1


async def test_revoke_own_key(client, key_client, raw_conn):
    member = await create_user(raw_conn)
    key = (await _generate(client, member))["key"]

    response = await client.delete("/api/api-keys/me", headers=auth_headers(member))
    fetched = await client.get("/api/api-keys/me", headers=auth_headers(member))

    assert response.status_code == 200, response.text
    assert fetched.json()["payload"] is None
    assert (await key_client.get("/whoami", headers=_bearer(key))).status_code == 401


async def test_revoke_without_key_is_404(client, raw_conn):
    member = await create_user(raw_conn)

    response = await client.delete("/api/api-keys/me", headers=auth_headers(member))

    assert response.status_code == 404, response.text


# --- 4.2: owner management ---------------------------------------------------


async def test_owner_lists_keys_without_full_key(client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")
    member = await create_user(raw_conn, username="alice")
    await create_user(raw_conn, username="no-key")
    key = (await _generate(client, member))["key"]

    response = await client.get("/api/api-keys", headers=auth_headers(owner))

    assert response.status_code == 200, response.text
    payload = response.json()["payload"]
    assert payload["total"] == 1
    item = payload["items"][0]
    assert item["userId"] == member
    assert item["username"] == "alice"
    assert item["prefix"] == key[:12]
    assert key not in response.text


async def test_owner_revokes_another_users_key(client, key_client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")
    member = await create_user(raw_conn)
    key = (await _generate(client, member))["key"]

    response = await client.delete(
        f"/api/api-keys/{member}", headers=auth_headers(owner)
    )

    assert response.status_code == 200, response.text
    assert (await key_client.get("/whoami", headers=_bearer(key))).status_code == 401


async def test_owner_revoke_missing_key_is_404(client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")
    member = await create_user(raw_conn)

    response = await client.delete(
        f"/api/api-keys/{member}", headers=auth_headers(owner)
    )

    assert response.status_code == 404, response.text


@pytest.mark.parametrize("role", ["member", "admin"])
async def test_only_owner_lists_and_revokes_others(client, key_client, raw_conn, role):
    actor = await create_user(raw_conn, role_name=role)
    member = await create_user(raw_conn)
    key = (await _generate(client, member))["key"]

    listed = await client.get("/api/api-keys", headers=auth_headers(actor))
    revoked = await client.delete(
        f"/api/api-keys/{member}", headers=auth_headers(actor)
    )

    assert listed.status_code == 403, listed.text
    assert revoked.status_code == 403, revoked.text
    assert (await key_client.get("/whoami", headers=_bearer(key))).status_code == 200


# --- 4.3: authentication by key ----------------------------------------------


@pytest.mark.parametrize("role", ["member", "admin", "owner"])
async def test_valid_key_resolves_user_and_role(client, key_client, raw_conn, role):
    user = await create_user(raw_conn, role_name=role)
    key = (await _generate(client, user))["key"]

    response = await key_client.get("/whoami", headers=_bearer(key))

    assert response.status_code == 200, response.text
    assert response.json()["id"] == user
    assert response.json()["role"] == role


async def test_missing_or_unknown_key_is_401(key_client):
    missing = await key_client.get("/whoami")
    unknown = await key_client.get("/whoami", headers=_bearer("ask_not-a-real-key"))

    assert missing.status_code == 401, missing.text
    assert unknown.status_code == 401, unknown.text


async def test_access_token_is_not_an_api_key(key_client, raw_conn):
    member = await create_user(raw_conn)

    response = await key_client.get("/whoami", headers=auth_headers(member))

    assert response.status_code == 401, response.text


async def test_deactivated_user_key_stops_and_resumes(client, key_client, raw_conn):
    member = await create_user(raw_conn)
    key = (await _generate(client, member))["key"]

    await raw_conn.execute("UPDATE users SET is_active = false WHERE id = $1", member)
    inactive = await key_client.get("/whoami", headers=_bearer(key))
    await raw_conn.execute("UPDATE users SET is_active = true WHERE id = $1", member)
    reactivated = await key_client.get("/whoami", headers=_bearer(key))

    assert inactive.status_code == 401, inactive.text
    assert reactivated.status_code == 200, reactivated.text


async def test_role_change_takes_effect_on_next_call(client, key_client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    key = (await _generate(client, admin))["key"]
    assert (await key_client.get("/admin-only", headers=_bearer(key))).status_code == 200

    await raw_conn.execute(
        "UPDATE users SET role_id = (SELECT id FROM role_types WHERE name = 'member')"
        " WHERE id = $1",
        admin,
    )
    response = await key_client.get("/admin-only", headers=_bearer(key))

    assert response.status_code == 403, response.text


async def test_last_used_at_is_throttled_to_a_minute(client, key_client, raw_conn):
    member = await create_user(raw_conn)
    key = (await _generate(client, member))["key"]

    await key_client.get("/whoami", headers=_bearer(key))
    first = await raw_conn.fetchval("SELECT last_used_at FROM api_keys")
    assert first is not None

    await raw_conn.execute(
        "UPDATE api_keys SET last_used_at = now() - interval '30 seconds'"
    )
    recent = await raw_conn.fetchval("SELECT last_used_at FROM api_keys")
    await key_client.get("/whoami", headers=_bearer(key))
    assert await raw_conn.fetchval("SELECT last_used_at FROM api_keys") == recent

    await raw_conn.execute(
        "UPDATE api_keys SET last_used_at = now() - interval '2 minutes'"
    )
    stale = await raw_conn.fetchval("SELECT last_used_at FROM api_keys")
    await key_client.get("/whoami", headers=_bearer(key))
    assert await raw_conn.fetchval("SELECT last_used_at FROM api_keys") > stale


async def test_owner_sees_last_use(client, key_client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner")
    member = await create_user(raw_conn)
    key = (await _generate(client, member))["key"]

    await key_client.get("/whoami", headers=_bearer(key))
    listed = await client.get("/api/api-keys", headers=auth_headers(owner))

    assert listed.json()["payload"]["items"][0]["lastUsedAt"] is not None


# --- 4.4: single-user mode and the web session -------------------------------


async def test_single_user_mode_still_requires_a_key(
    client, key_client, raw_conn, monkeypatch
):
    from packages.auth import auth_settings

    owner = await create_user(raw_conn, role_name="owner")
    key = (await _generate(client, owner))["key"]
    monkeypatch.setattr(auth_settings, "AUTH_ENABLED", False)

    without = await key_client.get("/whoami")
    with_key = await key_client.get("/whoami", headers=_bearer(key))

    assert without.status_code == 401, without.text
    assert with_key.status_code == 200, with_key.text
    assert with_key.json()["id"] == owner


async def test_api_key_does_not_open_session_routes(client, raw_conn):
    member = await create_user(raw_conn)
    key = (await _generate(client, member))["key"]

    response = await client.get("/api/users/me", headers=_bearer(key))

    assert response.status_code == 401, response.text
