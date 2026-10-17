"""Owner lifecycle (spec: instance-owner) and single-user mode (access-control)."""

import pytest
from factories import auth_headers, create_user


@pytest.fixture
def owner_env(monkeypatch):
    from packages.auth import auth_settings

    def set_env(username, password):
        monkeypatch.setattr(auth_settings, "OWNER_USERNAME", username)
        monkeypatch.setattr(auth_settings, "OWNER_PASSWORD", password)

    set_env(None, None)
    return set_env


async def _roles(raw_conn) -> dict:
    rows = await raw_conn.fetch(
        "SELECT u.username, r.name AS role, u.is_active FROM users u "
        "JOIN role_types r ON r.id = u.role_id"
    )
    return {r["username"]: (r["role"], r["is_active"]) for r in rows}


async def _set_created_at(raw_conn, username, when):
    await raw_conn.execute(
        "UPDATE users SET created_at = $2 WHERE username = $1", username, when
    )


# --- 4.2 ensure_owner -------------------------------------------------------


async def test_existing_owner_is_untouched_whatever_the_variables_say(
    raw_conn, owner_env
):
    from packages.auth import ensure_owner

    await create_user(raw_conn, username="boss", role_name="owner", password="secret1")
    before = await raw_conn.fetchval("SELECT password FROM users")
    owner_env("someone-else", "another-password")

    await ensure_owner()

    assert await _roles(raw_conn) == {"boss": ("owner", True)}
    assert await raw_conn.fetchval("SELECT password FROM users") == before


async def test_oldest_active_admin_is_promoted_even_if_renamed(raw_conn, owner_env):
    from datetime import datetime, timedelta, timezone

    from packages.auth import ensure_owner

    base = datetime.now(timezone.utc)
    await create_user(raw_conn, username="newer", role_name="admin")
    await create_user(raw_conn, username="renamed-original", role_name="admin")
    await create_user(raw_conn, username="plain", role_name="member")
    await _set_created_at(raw_conn, "renamed-original", base - timedelta(days=9))
    await _set_created_at(raw_conn, "newer", base - timedelta(days=1))
    owner_env("ignored", "ignored-password")

    await ensure_owner()

    roles = await _roles(raw_conn)
    assert roles["renamed-original"] == ("owner", True)
    assert roles["newer"] == ("admin", True)
    assert roles["plain"] == ("member", True)
    assert "ignored" not in roles


async def test_promotion_keeps_password_list_and_history(raw_conn, owner_env):
    from factories import create_anime
    from packages.auth import ensure_owner

    user_id = await create_user(raw_conn, role_name="admin", password="secret1")
    anime_id = await create_anime(raw_conn)
    await raw_conn.execute(
        "INSERT INTO user_save_anime (user_id, anime_id) VALUES ($1, $2)",
        __import__("uuid").UUID(user_id),
        anime_id,
    )
    before = await raw_conn.fetchval("SELECT password FROM users")

    await ensure_owner()

    assert await raw_conn.fetchval("SELECT password FROM users") == before
    assert await raw_conn.fetchval("SELECT count(*) FROM user_save_anime") == 1


async def test_disabled_oldest_admin_is_skipped(raw_conn, owner_env):
    from datetime import datetime, timedelta, timezone

    from packages.auth import ensure_owner

    base = datetime.now(timezone.utc)
    await create_user(raw_conn, username="old-off", role_name="admin", is_active=False)
    await create_user(raw_conn, username="next-on", role_name="admin")
    await _set_created_at(raw_conn, "old-off", base - timedelta(days=9))
    await _set_created_at(raw_conn, "next-on", base - timedelta(days=1))

    await ensure_owner()

    roles = await _roles(raw_conn)
    assert roles["next-on"] == ("owner", True)
    assert roles["old-off"] == ("admin", False)


async def test_only_disabled_admins_means_creating_the_owner_from_env(
    raw_conn, owner_env
):
    from packages.auth import ensure_owner

    await create_user(raw_conn, username="off", role_name="admin", is_active=False)
    owner_env("fresh-owner", "secret-pass")

    await ensure_owner()

    roles = await _roles(raw_conn)
    assert roles["fresh-owner"] == ("owner", True)
    assert roles["off"] == ("admin", False)


async def test_owner_is_created_from_the_environment(raw_conn, owner_env):
    from packages.auth import ensure_owner, verify_password

    owner_env("first-owner", "secret-pass")

    await ensure_owner()

    assert await _roles(raw_conn) == {"first-owner": ("owner", True)}
    hashed = await raw_conn.fetchval("SELECT password FROM users")
    assert verify_password("secret-pass", hashed)
    assert "admin" not in await _roles(raw_conn)


@pytest.mark.parametrize(
    "username,password,variable",
    [
        ("someone", None, "OWNER_PASSWORD"),
        ("someone", "", "OWNER_PASSWORD"),
        (None, "secret-pass", "OWNER_USERNAME"),
        ("", "secret-pass", "OWNER_USERNAME"),
        ("someone", "123", "OWNER_PASSWORD"),
    ],
)
async def test_startup_fails_naming_the_bad_variable(
    raw_conn, owner_env, username, password, variable
):
    from packages.auth import OwnerBootstrapError, ensure_owner

    owner_env(username, password)

    with pytest.raises(OwnerBootstrapError, match=variable):
        await ensure_owner()

    assert await raw_conn.fetchval("SELECT count(*) FROM users") == 0


async def test_startup_fails_when_the_owner_name_is_taken(raw_conn, owner_env):
    from packages.auth import OwnerBootstrapError, ensure_owner

    await create_user(raw_conn, username="taken", role_name="member")
    owner_env("taken", "secret-pass")

    with pytest.raises(OwnerBootstrapError, match="already taken"):
        await ensure_owner()

    assert await _roles(raw_conn) == {"taken": ("member", True)}


async def test_concurrent_startups_end_with_a_single_owner(raw_conn, owner_env):
    import asyncio

    from packages.auth import ensure_owner

    owner_env("racer", "secret-pass")

    await asyncio.gather(ensure_owner(), ensure_owner(), ensure_owner())

    assert await _roles(raw_conn) == {"racer": ("owner", True)}


def test_no_default_credentials_remain_in_the_source():
    import pathlib

    src = pathlib.Path(__file__).resolve().parents[1] / "src"
    for path in src.rglob("*.py"):
        assert "admin123" not in path.read_text(encoding="utf-8"), path


# --- 4.3 single-user mode ---------------------------------------------------


async def test_single_user_mode_resolves_the_renamed_owner(
    client, raw_conn, monkeypatch
):
    from packages.auth import auth_settings

    await create_user(raw_conn, username="renamed-owner", role_name="owner")
    monkeypatch.setattr(auth_settings, "AUTH_ENABLED", False)

    me = await client.get("/api/users/me")
    users = await client.get("/api/users")

    assert me.status_code == 200
    assert me.json()["payload"]["username"] == "renamed-owner"
    assert me.json()["payload"]["role"] == "owner"
    assert users.status_code == 200


# --- 4.4 transfer -----------------------------------------------------------


async def _transfer(client, owner_id, target_id, password="secret1"):
    return await client.post(
        "/api/owner/transfer",
        json={"targetUserId": target_id, "currentPassword": password},
        headers=auth_headers(owner_id),
    )


async def test_transfer_succeeds(client, raw_conn):
    owner = await create_user(raw_conn, username="o", role_name="owner", password="secret1")
    target = await create_user(raw_conn, username="t", role_name="member")

    response = await _transfer(client, owner, target)

    assert response.status_code == 200
    roles = await _roles(raw_conn)
    assert roles["t"][0] == "owner" and roles["o"][0] == "admin"


async def test_transfer_with_wrong_password_changes_nothing(client, raw_conn):
    owner = await create_user(raw_conn, username="o", role_name="owner", password="secret1")
    target = await create_user(raw_conn, username="t", role_name="member")

    response = await _transfer(client, owner, target, password="wrong")

    assert response.status_code == 409
    roles = await _roles(raw_conn)
    assert roles["o"][0] == "owner" and roles["t"][0] == "member"


async def test_transfer_to_an_inactive_user_changes_nothing(client, raw_conn):
    owner = await create_user(raw_conn, username="o", role_name="owner", password="secret1")
    target = await create_user(raw_conn, username="t", role_name="member", is_active=False)

    response = await _transfer(client, owner, target)

    assert response.status_code == 400
    assert (await _roles(raw_conn))["o"][0] == "owner"


async def test_transfer_to_oneself_or_unknown_user_is_rejected(client, raw_conn):
    owner = await create_user(raw_conn, role_name="owner", password="secret1")

    assert (await _transfer(client, owner, owner)).status_code == 400
    assert (
        await _transfer(client, owner, "00000000-0000-0000-0000-000000000009")
    ).status_code == 404


async def test_admin_cannot_transfer(client, raw_conn):
    await create_user(raw_conn, username="o", role_name="owner")
    admin = await create_user(raw_conn, username="a", role_name="admin", password="secret1")
    target = await create_user(raw_conn, username="t", role_name="member")

    response = await _transfer(client, admin, target)

    assert response.status_code == 403
    assert (await _roles(raw_conn))["o"][0] == "owner"


async def test_transfer_is_atomic_when_the_second_step_fails(
    client, raw_conn, monkeypatch
):
    from packages.auth import repository as auth_repository

    owner = await create_user(raw_conn, username="o", role_name="owner", password="secret1")
    target = await create_user(raw_conn, username="t", role_name="member")

    real = auth_repository.set_user_role
    calls = []

    async def fail_on_second(conn, user_id, role_name):
        calls.append(role_name)
        if len(calls) == 2:
            raise RuntimeError("boom")
        await real(conn, user_id, role_name)

    monkeypatch.setattr(auth_repository, "set_user_role", fail_on_second)

    with pytest.raises(RuntimeError, match="boom"):
        await _transfer(client, owner, target)

    assert calls == ["admin", "owner"]
    roles = await _roles(raw_conn)
    assert roles["o"][0] == "owner" and roles["t"][0] == "member"
