"""Atomicity of the transactional paths in packages/episodes/service.py.

Both download paths enqueue in Dramatiq before opening their transaction
(design D6), so every test here uses `mock_dramatiq` regardless of where the
injected failure lands.
"""

import uuid

import pytest
from factories import create_anime, create_episode, create_user


async def _boom(*args, **kwargs):
    raise RuntimeError("boom")


async def test_download_episode_leaves_no_trace_on_mid_transaction_failure(
    mock_dramatiq, raw_conn, monkeypatch
):
    from packages.episodes import repository, service

    user_id = await create_user(raw_conn)
    anime_id = await create_anime(raw_conn)
    episode_id = await create_episode(raw_conn, anime_id=anime_id, ep_number=1)

    # First write is insert_user_episode_download; interrupt on the next one.
    monkeypatch.setattr(repository, "update_episode_job", _boom)

    with pytest.raises(RuntimeError, match="boom"):
        await service.download_anime_episode_controller(episode_id, False, user_id)

    download_count = await raw_conn.fetchval(
        "SELECT count(*) FROM user_download_episode WHERE user_id = $1 AND episode_id = $2",
        uuid.UUID(user_id),
        episode_id,
    )
    episode_row = await raw_conn.fetchrow(
        "SELECT job_id, status FROM episodes WHERE id = $1", episode_id
    )
    assert download_count == 0
    assert episode_row["job_id"] is None
    assert episode_row["status"] is None


async def test_bulk_download_continues_and_rolls_back_only_the_failed_episode(
    mock_dramatiq, raw_conn, monkeypatch
):
    from packages.episodes import repository, service

    user_id = await create_user(raw_conn)
    anime_id = await create_anime(raw_conn)
    failing_episode_id = await create_episode(raw_conn, anime_id=anime_id, ep_number=1)
    ok_episode_id = await create_episode(raw_conn, anime_id=anime_id, ep_number=2)

    original_update_job = repository.update_episode_job

    async def flaky_update_job(episode_id, job_id, status):
        if episode_id == failing_episode_id:
            raise RuntimeError("boom")
        return await original_update_job(episode_id, job_id, status)

    monkeypatch.setattr(repository, "update_episode_job", flaky_update_job)

    result = await service.download_anime_episode_bulk_controller(
        anime_id, [1, 2], user_id
    )

    by_number = {item.episode_number: item for item in result.items}
    assert by_number[1].success is False
    assert by_number[2].success is True

    failing_download_count = await raw_conn.fetchval(
        "SELECT count(*) FROM user_download_episode WHERE user_id = $1 AND episode_id = $2",
        uuid.UUID(user_id),
        failing_episode_id,
    )
    failing_row = await raw_conn.fetchrow(
        "SELECT job_id, status FROM episodes WHERE id = $1", failing_episode_id
    )
    assert failing_download_count == 0
    assert failing_row["job_id"] is None
    assert failing_row["status"] is None

    ok_download_count = await raw_conn.fetchval(
        "SELECT count(*) FROM user_download_episode WHERE user_id = $1 AND episode_id = $2",
        uuid.UUID(user_id),
        ok_episode_id,
    )
    ok_row = await raw_conn.fetchrow(
        "SELECT job_id, status FROM episodes WHERE id = $1", ok_episode_id
    )
    assert ok_download_count == 1
    assert ok_row["status"] == "PENDING"
    assert ok_row["job_id"] is not None


async def test_delete_anime_storage_leaves_no_trace_on_mid_transaction_failure(
    raw_conn, monkeypatch
):
    from packages.episodes import repository, service

    user_id = await create_user(raw_conn)
    anime_id = await create_anime(raw_conn, franchise_id=None, season=1)
    episode_id = await create_episode(
        raw_conn, anime_id=anime_id, ep_number=1, size=123, job_id="old-job", status="SUCCESS"
    )
    await raw_conn.execute(
        "INSERT INTO user_download_episode (user_id, episode_id) VALUES ($1, $2)",
        uuid.UUID(user_id),
        episode_id,
    )

    # First write is delete_user_downloads_for_episodes; interrupt on the next one.
    monkeypatch.setattr(repository, "reset_episodes_storage", _boom)

    with pytest.raises(RuntimeError, match="boom"):
        await service.delete_anime_storage_controller(anime_id, user_id)

    download_count = await raw_conn.fetchval(
        "SELECT count(*) FROM user_download_episode WHERE user_id = $1 AND episode_id = $2",
        uuid.UUID(user_id),
        episode_id,
    )
    episode_row = await raw_conn.fetchrow(
        "SELECT size, job_id, status FROM episodes WHERE id = $1", episode_id
    )
    assert download_count == 1
    assert episode_row["size"] == 123
    assert episode_row["job_id"] == "old-job"
    assert episode_row["status"] == "SUCCESS"
