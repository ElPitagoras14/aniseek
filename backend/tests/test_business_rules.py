"""Business rules that moved from FastAPI dependencies into the services
(mcp-server, design D5): the REST responses must stay the same, and the bulk
download now reports why each episode was not enqueued."""

import uuid
from datetime import datetime, timezone
from unittest.mock import Mock

from factories import auth_headers, create_anime, create_episode, create_user


async def _scraped_anime(raw_conn, anime_id: str = "rules-anime") -> str:
    return await create_anime(
        raw_conn,
        anime_id=anime_id,
        title="Rules",
        last_scraped_at=datetime.now(timezone.utc),
    )


async def test_save_twice_returns_409(client, raw_conn):
    user_id = await create_user(raw_conn)
    anime_id = await _scraped_anime(raw_conn)
    await raw_conn.execute(
        "INSERT INTO user_save_anime (user_id, anime_id) VALUES ($1, $2)",
        uuid.UUID(user_id),
        anime_id,
    )

    response = await client.put(
        f"/api/animes/{anime_id}/save", headers=auth_headers(user_id)
    )

    assert response.status_code == 409
    assert response.json()["message"] == "Anime already saved by user"


async def test_unsave_not_saved_returns_404(client, raw_conn):
    user_id = await create_user(raw_conn)
    anime_id = await _scraped_anime(raw_conn)

    response = await client.put(
        f"/api/animes/{anime_id}/unsave", headers=auth_headers(user_id)
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Anime not saved by user"


async def test_unsave_unknown_anime_returns_404(client, raw_conn):
    user_id = await create_user(raw_conn)

    response = await client.put(
        "/api/animes/does-not-exist/unsave", headers=auth_headers(user_id)
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Anime does-not-exist not found"


async def test_bulk_download_unknown_anime_returns_404(client, raw_conn, mock_dramatiq):
    user_id = await create_user(raw_conn)

    response = await client.post(
        "/api/episodes/does-not-exist/download/bulk",
        json=[1],
        headers=auth_headers(user_id),
    )

    assert response.status_code == 404
    mock_dramatiq["download_anime_episode"].assert_not_called()


async def test_bulk_download_reports_reason_per_episode(
    client, raw_conn, mock_dramatiq
):
    user_id = await create_user(raw_conn)
    anime_id = await _scraped_anime(raw_conn)
    for n in (1, 2, 3):
        await create_episode(raw_conn, anime_id=anime_id, ep_number=n)
    downloaded_id = await raw_conn.fetchval(
        "SELECT id FROM episodes WHERE anime_id = $1 AND ep_number = 2", anime_id
    )
    await raw_conn.execute(
        "INSERT INTO user_download_episode (user_id, episode_id) VALUES ($1, $2)",
        uuid.UUID(user_id),
        downloaded_id,
    )

    def send(anime, ep_number, user):
        if ep_number == 3:
            raise RuntimeError("broker down")
        return Mock(message_id=f"job-{ep_number}")

    mock_dramatiq["download_anime_episode"].side_effect = send

    response = await client.post(
        f"/api/episodes/{anime_id}/download/bulk",
        json=[1, 2, 3, 99],
        headers=auth_headers(user_id),
    )

    assert response.status_code == 200
    # This endpoint answers in snake_case (pre-existing behavior).
    items = {i["episode_number"]: i for i in response.json()["payload"]["items"]}
    assert items[1] == {
        "job_id": "job-1",
        "episode_number": 1,
        "success": True,
        "reason": None,
    }
    assert items[2]["success"] is False and items[2]["reason"] == "already_downloaded"
    assert items[3]["success"] is False and items[3]["reason"] == "enqueue_failed"
    assert items[99]["success"] is False and items[99]["reason"] == "not_found"
