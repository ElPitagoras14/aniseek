"""The MCP server at /api/mcp (specs: mcp-server, access-control).

Requests go through the real app over ASGI, as JSON-RPC over Streamable HTTP.
The `client` fixture runs no lifespan, so each test starts the MCP session
manager itself with `mcp_running()`: the manager's task group must be entered
and left in the same task, which an async fixture does not guarantee."""

import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import pytest
from factories import auth_headers, create_anime, create_episode, create_user

MCP_URL = "/api/mcp"
_HEADERS = {"Accept": "application/json, text/event-stream"}


@asynccontextmanager
async def mcp_running():
    from mcp_server import mcp_lifespan

    async with mcp_lifespan():
        yield


async def _set_mcp(raw_conn, enabled: bool) -> None:
    await raw_conn.execute("UPDATE instance_settings SET mcp_enabled = $1", enabled)


async def _key(client, user_id: str) -> str:
    response = await client.post("/api/api-keys/me", headers=auth_headers(user_id))
    assert response.status_code == 200, response.text
    return response.json()["payload"]["key"]


_ids = iter(range(1, 1_000_000))


async def _rpc(client, key: str | None, method: str, params: dict | None = None):
    headers = dict(_HEADERS)
    if key is not None:
        headers["Authorization"] = f"Bearer {key}"
    return await client.post(
        MCP_URL,
        json={
            "jsonrpc": "2.0",
            "id": next(_ids),
            "method": method,
            "params": params or {},
        },
        headers=headers,
    )


async def _tool_names(client, key: str) -> set[str]:
    response = await _rpc(client, key, "tools/list")
    assert response.status_code == 200, response.text
    return {t["name"] for t in response.json()["result"]["tools"]}


async def _call(client, key: str, name: str, arguments: dict | None = None) -> dict:
    response = await _rpc(
        client, key, "tools/call", {"name": name, "arguments": arguments or {}}
    )
    assert response.status_code == 200, response.text
    return response.json()["result"]


def _error_text(result: dict) -> str:
    assert result["isError"] is True, result
    return result["content"][0]["text"]


@pytest.fixture
async def member(raw_conn):
    return await create_user(raw_conn, role_name="member")


async def _scraped_anime(raw_conn, anime_id: str, **fields) -> str:
    fields.setdefault("last_scraped_at", datetime.now(timezone.utc))
    fields.setdefault("type", "TV")
    fields.setdefault("poster", "https://example.test/poster.jpg")
    fields.setdefault("description", "")
    fields.setdefault("is_finished", False)
    return await create_anime(raw_conn, anime_id=anime_id, title=anime_id, **fields)


# --- 5.1 switch ---------------------------------------------------------------


async def test_mcp_disabled_answers_404_with_and_without_key(client, raw_conn, member):
    key = await _key(client, member)

    async with mcp_running():
        with_key = await _rpc(client, key, "tools/list")
        without_key = await _rpc(client, None, "tools/list")

    assert with_key.status_code == 404
    assert without_key.status_code == 404


async def test_owner_enables_mcp_without_restart(client, raw_conn, member):
    owner = await create_user(raw_conn, role_name="owner")
    key = await _key(client, member)

    async with mcp_running():
        assert (await _rpc(client, key, "tools/list")).status_code == 404

        response = await client.put(
            "/api/settings/mcp", json={"enabled": True}, headers=auth_headers(owner)
        )
        assert response.status_code == 200
        assert response.json()["payload"]["mcpEnabled"] is True

        assert (await _rpc(client, key, "tools/list")).status_code == 200


@pytest.mark.parametrize("role", ["member", "admin"])
async def test_only_the_owner_changes_the_mcp_switch(client, raw_conn, role):
    user = await create_user(raw_conn, role_name=role)

    response = await client.put(
        "/api/settings/mcp", json={"enabled": True}, headers=auth_headers(user)
    )

    assert response.status_code == 403
    assert await raw_conn.fetchval("SELECT mcp_enabled FROM instance_settings") is False


async def test_settings_expose_the_mcp_state(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    await _set_mcp(raw_conn, True)

    response = await client.get("/api/settings", headers=auth_headers(admin))

    assert response.json()["payload"]["mcpEnabled"] is True


async def test_any_user_reads_whether_mcp_is_enabled(client, raw_conn, member):
    off = await client.get("/api/settings/mcp", headers=auth_headers(member))
    await _set_mcp(raw_conn, True)
    on = await client.get("/api/settings/mcp", headers=auth_headers(member))
    anonymous = await client.get("/api/settings/mcp")

    assert off.json()["payload"] == {"enabled": False}
    assert on.json()["payload"] == {"enabled": True}
    assert anonymous.status_code in (401, 403)


async def test_keys_survive_turning_mcp_off_and_on(client, raw_conn, member):
    key = await _key(client, member)

    async with mcp_running():
        await _set_mcp(raw_conn, True)
        assert (await _rpc(client, key, "tools/list")).status_code == 200
        await _set_mcp(raw_conn, False)
        assert (await _rpc(client, key, "tools/list")).status_code == 404
        await _set_mcp(raw_conn, True)
        assert (await _rpc(client, key, "tools/list")).status_code == 200


# --- 5.2 authentication -------------------------------------------------------


async def test_request_without_key_is_401(client, raw_conn):
    await _set_mcp(raw_conn, True)

    async with mcp_running():
        response = await _rpc(client, None, "tools/list")

    assert response.status_code == 401


async def test_web_session_token_is_401(client, raw_conn, member):
    await _set_mcp(raw_conn, True)
    session_token = auth_headers(member)["Authorization"].removeprefix("Bearer ")

    async with mcp_running():
        response = await _rpc(client, session_token, "tools/list")

    assert response.status_code == 401


async def test_revoked_key_is_401_on_the_next_call(client, raw_conn, member):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)

    async with mcp_running():
        assert (await _rpc(client, key, "tools/list")).status_code == 200
        await client.delete("/api/api-keys/me", headers=auth_headers(member))
        assert (await _rpc(client, key, "tools/list")).status_code == 401


async def test_deactivated_user_is_401(client, raw_conn, member):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)
    await raw_conn.execute(
        "UPDATE users SET is_active = false WHERE id = $1", uuid.UUID(member)
    )

    async with mcp_running():
        response = await _rpc(client, key, "tools/list")

    assert response.status_code == 401


async def test_single_user_mode_still_requires_a_key(client, raw_conn, monkeypatch):
    from packages.auth.config import auth_settings

    owner = await create_user(raw_conn, role_name="owner")
    await _set_mcp(raw_conn, True)
    key = await _key(client, owner)
    monkeypatch.setattr(auth_settings, "AUTH_ENABLED", False)

    async with mcp_running():
        without_key = await _rpc(client, None, "tools/list")
        with_key = await _rpc(client, key, "tools/list")

    assert without_key.status_code == 401
    assert with_key.status_code == 200


# --- 5.3 protocol end to end ------------------------------------------------------


async def test_initialize_list_and_call_over_http(client, raw_conn, member):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)
    anime_id = await _scraped_anime(raw_conn, "saved-one")
    await raw_conn.execute(
        "INSERT INTO user_save_anime (user_id, anime_id) VALUES ($1, $2)",
        uuid.UUID(member),
        anime_id,
    )

    async with mcp_running():
        init = await _rpc(
            client,
            key,
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "0"},
            },
        )
        listed = await _rpc(client, key, "tools/list")
        result = await _call(client, key, "list_saved")

    assert init.status_code == 200
    assert init.json()["result"]["serverInfo"]["name"] == "aniseek"

    tools = {t["name"]: t for t in listed.json()["result"]["tools"]}
    assert tools["list_saved"]["annotations"]["readOnlyHint"] is True
    assert tools["download_episodes"]["annotations"]["readOnlyHint"] is False
    assert tools["search_anime"]["annotations"]["openWorldHint"] is True

    assert result["isError"] is False
    assert result["structuredContent"]["items"][0]["id"] == "animeav1:saved-one"


# --- 5.4 roles ------------------------------------------------------------------


async def test_member_does_not_see_or_run_delete_anime_files(client, raw_conn, member):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)
    anime_id = await _scraped_anime(raw_conn, "keep-me")
    await create_episode(raw_conn, anime_id=anime_id, ep_number=1, status="SUCCESS")

    async with mcp_running():
        names = await _tool_names(client, key)
        result = await _call(
            client, key, "delete_anime_files", {"anime_id": "animeav1:keep-me"}
        )

    assert "delete_anime_files" not in names
    assert "Insufficient permissions" in _error_text(result)
    assert (
        await raw_conn.fetchval(
            "SELECT status FROM episodes WHERE anime_id = $1", anime_id
        )
        == "SUCCESS"
    )


async def test_admin_sees_the_destructive_tool(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    await _set_mcp(raw_conn, True)
    key = await _key(client, admin)

    async with mcp_running():
        listed = await _rpc(client, key, "tools/list")

    tools = {t["name"]: t for t in listed.json()["result"]["tools"]}
    assert tools["delete_anime_files"]["annotations"]["destructiveHint"] is True


async def test_demoted_admin_is_rejected_on_the_next_call(client, raw_conn):
    admin = await create_user(raw_conn, role_name="admin")
    await _set_mcp(raw_conn, True)
    key = await _key(client, admin)
    await _scraped_anime(raw_conn, "demote")

    async with mcp_running():
        assert "delete_anime_files" in await _tool_names(client, key)
        await raw_conn.execute(
            "UPDATE users SET role_id = (SELECT id FROM role_types WHERE name = 'member')"
            " WHERE id = $1",
            uuid.UUID(admin),
        )
        result = await _call(
            client, key, "delete_anime_files", {"anime_id": "animeav1:demote"}
        )

    assert "Insufficient permissions" in _error_text(result)


# --- 5.5 rules and results ----------------------------------------------------------


async def test_refresh_within_cooldown_is_an_error(client, raw_conn, member, monkeypatch):
    from packages.animes import service

    await _set_mcp(raw_conn, True)
    key = await _key(client, member)
    await _scraped_anime(
        raw_conn,
        "recent",
        last_scraped_at=datetime.now(timezone.utc) - timedelta(minutes=2),
    )

    async def no_sync(anime_id):
        raise AssertionError("must not sync during the cooldown")

    monkeypatch.setattr(service, "sync_anime", no_sync)

    async with mcp_running():
        result = await _call(client, key, "refresh_anime", {"anime_id": "animeav1:recent"})

    assert "Please wait" in _error_text(result)


async def test_save_twice_and_unsave_unsaved_are_errors(client, raw_conn, member):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)
    await _scraped_anime(raw_conn, "lib")

    async with mcp_running():
        first = await _call(client, key, "save_anime", {"anime_id": "animeav1:lib"})
        second = await _call(client, key, "save_anime", {"anime_id": "animeav1:lib"})
        await _call(client, key, "unsave_anime", {"anime_id": "animeav1:lib"})
        again = await _call(client, key, "unsave_anime", {"anime_id": "animeav1:lib"})

    assert first["structuredContent"] == {"anime_id": "animeav1:lib", "is_saved": True}
    assert "already saved" in _error_text(second)
    assert "not saved" in _error_text(again)


async def test_download_of_unknown_anime_is_an_error(
    client, raw_conn, member, mock_dramatiq
):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)

    async with mcp_running():
        result = await _call(
            client,
            key,
            "download_episodes",
            {"anime_id": "animeav1:nope", "episodes": [1]},
        )

    assert "not found" in _error_text(result)
    mock_dramatiq["download_anime_episode"].assert_not_called()


async def _anime_with_episodes(raw_conn, anime_id: str, count: int) -> str:
    await _scraped_anime(raw_conn, anime_id)
    for n in range(1, count + 1):
        await create_episode(raw_conn, anime_id=anime_id, ep_number=n)
    return anime_id


async def _mark_requested(raw_conn, user_id: str, anime_id: str, numbers) -> None:
    for n in numbers:
        episode_id = await raw_conn.fetchval(
            "SELECT id FROM episodes WHERE anime_id = $1 AND ep_number = $2",
            anime_id,
            n,
        )
        await raw_conn.execute(
            "INSERT INTO user_download_episode (user_id, episode_id) VALUES ($1, $2)",
            uuid.UUID(user_id),
            episode_id,
        )


async def test_more_than_25_new_episodes_are_rejected_whole(
    client, raw_conn, member, mock_dramatiq
):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)
    await _anime_with_episodes(raw_conn, "long", 30)

    async with mcp_running():
        result = await _call(
            client,
            key,
            "download_episodes",
            {"anime_id": "animeav1:long", "episodes": list(range(1, 31))},
        )

    assert "Split the request" in _error_text(result)
    mock_dramatiq["download_anime_episode"].assert_not_called()


async def test_already_requested_episodes_do_not_count_against_the_cap(
    client, raw_conn, member, mock_dramatiq
):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)
    await _anime_with_episodes(raw_conn, "long", 30)
    await _mark_requested(raw_conn, member, "long", range(1, 11))

    async with mcp_running():
        result = await _call(
            client,
            key,
            "download_episodes",
            {"anime_id": "animeav1:long", "episodes": list(range(1, 31))},
        )

    data = result["structuredContent"]
    states = {e["number"]: e["state"] for e in data["episodes"]}
    assert data["enqueued"] == 20
    assert all(states[n] == "already_downloaded" for n in range(1, 11))
    assert all(states[n] == "enqueued" for n in range(11, 31))
    assert mock_dramatiq["download_anime_episode"].call_count == 20


async def test_unknown_episode_is_reported(client, raw_conn, member, mock_dramatiq):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)
    await _anime_with_episodes(raw_conn, "short", 12)

    async with mcp_running():
        result = await _call(
            client,
            key,
            "download_episodes",
            {"anime_id": "animeav1:short", "episodes": [1, 9999, 1]},
        )

    episodes = result["structuredContent"]["episodes"]
    assert episodes == [
        {"number": 1, "state": "enqueued"},
        {"number": 9999, "state": "not_found"},
    ]


async def test_download_status_after_success(client, raw_conn, member, mock_dramatiq):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)
    await _anime_with_episodes(raw_conn, "done", 3)

    async with mcp_running():
        await _call(
            client,
            key,
            "download_episodes",
            {"anime_id": "animeav1:done", "episodes": [1]},
        )
        # The worker finishes: status SUCCESS and the job id cleared.
        await raw_conn.execute(
            "UPDATE episodes SET status = 'SUCCESS', job_id = NULL"
            " WHERE anime_id = 'done' AND ep_number = 1"
        )
        result = await _call(
            client,
            key,
            "get_download_status",
            {"anime_id": "animeav1:done", "episodes": [1, 2, 50]},
        )

    assert result["structuredContent"]["episodes"] == [
        {"number": 1, "status": "downloaded", "requested_by_user": True},
        {"number": 2, "status": "not_downloaded", "requested_by_user": False},
        {"number": 50, "status": "not_found", "requested_by_user": False},
    ]


async def test_ids_carry_the_provider_including_relations(client, raw_conn, member):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)
    await _anime_with_episodes(raw_conn, "main-show", 2)
    await _scraped_anime(raw_conn, "the-sequel")
    await raw_conn.execute(
        "INSERT INTO anime_relations (anime_id, related_anime_id, type_related_id)"
        " VALUES ('main-show', 'the-sequel', (SELECT id FROM related_types LIMIT 1))"
    )

    async with mcp_running():
        result = await _call(
            client, key, "get_anime", {"anime_id": "animeav1:main-show"}
        )

    data = result["structuredContent"]
    assert data["id"] == "animeav1:main-show"
    assert [r["id"] for r in data["related"]] == ["animeav1:the-sequel"]
    assert [e["number"] for e in data["episodes"]] == [1, 2]


@pytest.mark.parametrize(
    "anime_id,expected",
    [
        ("jkanime:one-piece", "Supported providers"),
        ("one-piece", "<provider>:<slug>"),
        ("animeav1:", "<provider>:<slug>"),
    ],
)
async def test_invalid_ids_are_rejected(client, raw_conn, member, anime_id, expected):
    await _set_mcp(raw_conn, True)
    key = await _key(client, member)

    async with mcp_running():
        result = await _call(client, key, "get_anime", {"anime_id": anime_id})

    assert expected in _error_text(result)


# --- 3.5 ids (unit) -------------------------------------------------------------


def test_parse_and_format_anime_id():
    from mcp_server.ids import format_anime_id, parse_anime_id

    assert parse_anime_id("animeav1:one-piece") == "one-piece"
    assert format_anime_id("one-piece") == "animeav1:one-piece"


@pytest.mark.parametrize("value", ["one-piece", "jkanime:x", "animeav1:", "a:b:c", ""])
def test_parse_anime_id_rejects(value):
    from mcp.server.mcpserver.exceptions import ToolError

    from mcp_server.ids import parse_anime_id

    with pytest.raises(ToolError):
        parse_anime_id(value)
