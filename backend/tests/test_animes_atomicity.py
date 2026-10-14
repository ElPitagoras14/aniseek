"""Atomicity of the single sync flow in packages/animes/service.py.

The failure is injected by substituting one of the repository calls
_persist_snapshot makes after its first write, so it fails without depending
on a schema constraint. The scrape is always substituted, so no test ever
reaches the network.
"""

from datetime import datetime, timezone

import pytest
from ani_scrapy.core import AnimeInfo, AnimeType, RelatedInfo, RelatedType
from factories import create_anime


def _fake_anime_info(anime_id: str, **overrides) -> AnimeInfo:
    fields = {
        "id": anime_id,
        "title": "Scraped Title",
        "type": AnimeType.TV,
        "poster": "https://example.test/poster.png",
        "description": "Scraped description",
        "is_finished": False,
        "genres": ["Action"],
        "related_info": [],
        "next_episode_date": None,
        "episodes": [],
    }
    fields.update(overrides)
    return AnimeInfo(**fields)


def _fake_scrape(result):
    async def _scrape(*args, **kwargs):
        return result

    return _scrape


async def _boom(*args, **kwargs):
    raise RuntimeError("boom")


async def test_sync_of_new_anime_leaves_no_trace_on_mid_transaction_failure(
    raw_conn, monkeypatch
):
    from packages.animes import repository, service

    anime_id = "atomic-add-anime"
    monkeypatch.setattr(service, "scrape_anime_info", _fake_scrape(_fake_anime_info(anime_id)))
    # First write is upsert_scraped_anime; interrupt on the next one.
    monkeypatch.setattr(repository, "insert_genres", _boom)

    with pytest.raises(RuntimeError, match="boom"):
        await service.sync_anime(anime_id)

    row = await raw_conn.fetchrow("SELECT id FROM animes WHERE id = $1", anime_id)
    assert row is None


async def test_sync_of_existing_anime_keeps_previous_state_on_mid_transaction_failure(
    raw_conn, monkeypatch
):
    from packages.animes import repository, service

    anime_id = "atomic-update-anime"
    previous_last_scraped = datetime(2020, 1, 1, tzinfo=timezone.utc)
    await create_anime(
        raw_conn,
        anime_id=anime_id,
        title="Previous Title",
        description="Previous description",
        poster="https://example.test/previous.png",
        type="TV",
        is_finished=False,
        week_day="Monday",
        last_scraped_at=previous_last_scraped,
    )
    await create_anime(raw_conn, anime_id="related-anime", title="Related")

    fake_info = _fake_anime_info(
        anime_id,
        title="New Title",
        description="New description",
        poster="https://example.test/new.png",
        is_finished=True,
        related_info=[RelatedInfo(id="related-anime", title="Related", type=RelatedType.SEQUEL)],
    )
    monkeypatch.setattr(service, "scrape_anime_info", _fake_scrape(fake_info))
    # upsert_scraped_anime and insert_genres have already written by now;
    # interrupt on the relations write.
    monkeypatch.setattr(repository, "upsert_relations", _boom)

    with pytest.raises(RuntimeError, match="boom"):
        await service.sync_anime(anime_id)

    row = await raw_conn.fetchrow(
        """
        SELECT title, description, poster, is_finished, week_day, last_scraped_at
        FROM animes WHERE id = $1
        """,
        anime_id,
    )
    assert row["title"] == "Previous Title"
    assert row["description"] == "Previous description"
    assert row["poster"] == "https://example.test/previous.png"
    assert row["is_finished"] is False
    assert row["week_day"] == "Monday"
    assert row["last_scraped_at"] == previous_last_scraped
    genres = await raw_conn.fetch("SELECT name FROM genres WHERE anime_id = $1", anime_id)
    assert genres == []
