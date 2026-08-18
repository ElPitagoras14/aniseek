"""Atomicity of the two transactional paths in packages/animes/service.py.

Design D6: the failure is injected by substituting one of the repository calls
the transaction makes after its first write, so it fails without depending on
a schema constraint. Design D6 also notes the scraping calls have to be
substituted regardless of where the failure lands, so no test ever reaches the
network.

decouple-anime-scrape-persist: update_anime_info now runs both scrapes (and
the rate-limit sleep between them) before opening its write transaction, so
scrape_new_episodes and asyncio.sleep must be substituted too — they're no
longer shielded by a failure injected inside the transaction.
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


async def _no_sleep(*args, **kwargs) -> None:
    pass


async def _boom(*args, **kwargs):
    raise RuntimeError("boom")


async def test_add_new_anime_leaves_no_trace_on_mid_transaction_failure(
    raw_conn, monkeypatch
):
    from packages.animes import repository, service

    anime_id = "atomic-add-anime"
    monkeypatch.setattr(service, "scrape_anime_info", _fake_scrape(_fake_anime_info(anime_id)))
    # First write is upsert_scraped_anime; interrupt on the next one.
    monkeypatch.setattr(repository, "insert_genres", _boom)

    with pytest.raises(RuntimeError, match="boom"):
        await service.add_new_anime("https://example.test", anime_id)

    row = await raw_conn.fetchrow("SELECT id FROM animes WHERE id = $1", anime_id)
    assert row is None


async def test_update_anime_info_keeps_previous_fields_on_mid_transaction_failure(
    raw_conn, monkeypatch
):
    import asyncio

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
    # Both scrapes and the rate-limit sleep now run before the write
    # transaction opens, so they must be substituted regardless of where the
    # failure lands inside that transaction.
    monkeypatch.setattr(service, "scrape_new_episodes", _fake_scrape([]))
    monkeypatch.setattr(asyncio, "sleep", _no_sleep)
    # First write is update_anime_fields; interrupt right after it, in the
    # related_info loop.
    monkeypatch.setattr(repository, "insert_dummy_anime", _boom)

    with pytest.raises(RuntimeError, match="boom"):
        await service.update_anime_info("https://example.test", anime_id)

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
