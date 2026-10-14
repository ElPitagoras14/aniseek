"""Behavior of the unified anime sync (change unify-anime-sync): batch
persistence, refresh semantics, the 'scraped' rule, single-flight, the
response contract and provider error translation."""

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from ani_scrapy.core import (
    EpisodeInfo,
    RelatedInfo,
    RelatedType,
    ScraperBlockedError,
    ScraperHTTPError,
    ScraperNotFoundError,
    ScraperParseError,
    ScraperTimeoutError,
)
from factories import create_anime, create_episode, create_user

from test_animes_atomicity import _fake_anime_info


def _episodes(anime_id: str, n: int) -> list[EpisodeInfo]:
    return [
        EpisodeInfo(episode_number=i, anime_id=anime_id, image_preview=f"p{i}.png")
        for i in range(1, n + 1)
    ]


def _counting_scrape(monkeypatch, result, counter: list, delay: float = 0):
    from packages.animes import service

    async def _scrape(*args, **kwargs):
        counter.append(1)
        if delay:
            await asyncio.sleep(delay)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(service, "scrape_anime_info", _scrape)


# --- repository.upsert_relations -------------------------------------------


async def test_upsert_relations_twice_does_not_duplicate_rows(raw_conn):
    from database.client import engine
    from packages.animes import repository

    await create_anime(raw_conn, anime_id="main-anime", title="Main")
    placeholders = [{"id": "rel-1", "title": "Rel 1"}, {"id": "rel-2", "title": "Rel 2"}]
    relations = [
        {"anime_id": "main-anime", "related_anime_id": "rel-1", "type_related_id": 2},
        {"anime_id": "main-anime", "related_anime_id": "rel-2", "type_related_id": 1},
    ]

    for _ in range(2):
        async with engine.begin() as conn:
            await repository.upsert_relations(conn, placeholders, relations)

    assert await raw_conn.fetchval("SELECT count(*) FROM anime_relations") == 2
    assert await raw_conn.fetchval("SELECT count(*) FROM animes WHERE id LIKE 'rel-%'") == 2


# --- sync persistence -------------------------------------------------------


async def test_sync_persists_anime_genres_relations_and_episodes(raw_conn, monkeypatch):
    from packages.animes import service

    anime_id = "full-sync"
    info = _fake_anime_info(
        anime_id,
        genres=["Action", "Drama"],
        related_info=[RelatedInfo(id="seq", title="Seq", type=RelatedType.SEQUEL)],
        episodes=_episodes(anime_id, 3),
    )
    _counting_scrape(monkeypatch, info, [])

    await service.sync_anime(anime_id)

    row = await raw_conn.fetchrow(
        "SELECT title, last_scraped_at FROM animes WHERE id = $1", anime_id
    )
    assert row["title"] == "Scraped Title" and row["last_scraped_at"] is not None
    assert await raw_conn.fetchval("SELECT count(*) FROM genres WHERE anime_id = $1", anime_id) == 2
    assert (
        await raw_conn.fetchval("SELECT count(*) FROM anime_relations WHERE anime_id = $1", anime_id)
        == 1
    )
    # the related anime stays a placeholder
    assert await raw_conn.fetchval("SELECT last_scraped_at FROM animes WHERE id = 'seq'") is None
    urls = await raw_conn.fetch(
        "SELECT url FROM episodes WHERE anime_id = $1 ORDER BY ep_number", anime_id
    )
    assert [r["url"] for r in urls] == [
        f"https://animeav1.com/media/{anime_id}/{i}" for i in (1, 2, 3)
    ]


async def test_refresh_adds_new_episodes_without_duplicating_existing(raw_conn, monkeypatch):
    from packages.animes import service

    anime_id = "refresh-anime"
    calls: list = []
    _counting_scrape(
        monkeypatch, _fake_anime_info(anime_id, episodes=_episodes(anime_id, 10)), calls
    )
    await service.sync_anime(anime_id)
    count_sql = "SELECT count(*) FROM episodes WHERE anime_id = $1"
    assert await raw_conn.fetchval(count_sql, anime_id) == 10

    _counting_scrape(
        monkeypatch, _fake_anime_info(anime_id, episodes=_episodes(anime_id, 12)), calls
    )
    await service.sync_anime(anime_id)
    assert await raw_conn.fetchval(count_sql, anime_id) == 12

    # a refresh with no news leaves collections unchanged
    await service.sync_anime(anime_id)
    assert await raw_conn.fetchval(count_sql, anime_id) == 12
    assert await raw_conn.fetchval("SELECT count(*) FROM genres WHERE anime_id = $1", anime_id) == 1


async def test_sync_with_unknown_relation_type_skips_it_and_succeeds(raw_conn, monkeypatch):
    from packages.animes import service

    anime_id = "unknown-rel"
    base = _fake_anime_info(anime_id)
    info = SimpleNamespace(
        id=anime_id,
        title=base.title,
        description=base.description,
        poster=base.poster,
        type=base.type,
        is_finished=base.is_finished,
        next_episode_date=None,
        genres=[],
        episodes=[],
        related_info=[
            RelatedInfo(id="seq", title="Seq", type=RelatedType.SEQUEL),
            SimpleNamespace(id="odd", title="Odd", type=SimpleNamespace(value="Spin-off")),
        ],
    )
    _counting_scrape(monkeypatch, info, [])

    await service.sync_anime(anime_id)

    rels = await raw_conn.fetch(
        "SELECT related_anime_id FROM anime_relations WHERE anime_id = $1", anime_id
    )
    assert [r["related_anime_id"] for r in rels] == ["seq"]
    assert await raw_conn.fetchval("SELECT count(*) FROM animes WHERE id = 'odd'") == 0


# --- "scraped" rule ---------------------------------------------------------


def test_is_scraped_rule():
    from packages.animes.service import is_scraped

    assert not is_scraped(None)
    assert not is_scraped({"last_scraped_at": None})
    assert is_scraped({"last_scraped_at": datetime.now(timezone.utc)})


async def test_get_anime_on_placeholder_triggers_sync(raw_conn, monkeypatch):
    from packages.animes import service

    anime_id = "placeholder-anime"
    await create_anime(raw_conn, anime_id=anime_id, title="Placeholder")
    user_id = await create_user(raw_conn)
    calls: list = []
    _counting_scrape(
        monkeypatch, _fake_anime_info(anime_id, episodes=_episodes(anime_id, 2)), calls
    )

    result = await service.get_anime_controller(anime_id, user_id)

    assert len(calls) == 1
    assert result.title == "Scraped Title"
    assert len(result.episodes) == 2


async def test_get_anime_already_scraped_does_not_sync(raw_conn, monkeypatch):
    from packages.animes import service

    anime_id = "scraped-anime"
    await create_anime(
        raw_conn,
        anime_id=anime_id,
        title="T",
        description="d",
        poster="p",
        type="TV",
        is_finished=False,
        last_scraped_at=datetime.now(timezone.utc),
    )
    user_id = await create_user(raw_conn)
    calls: list = []
    _counting_scrape(monkeypatch, _fake_anime_info(anime_id), calls)

    await service.get_anime_controller(anime_id, user_id)

    assert calls == []


async def test_save_anime_on_placeholder_syncs_before_saving(raw_conn, monkeypatch):
    from packages.animes import service

    anime_id = "save-placeholder"
    await create_anime(raw_conn, anime_id=anime_id, title="Placeholder")
    user_id = await create_user(raw_conn)
    calls: list = []
    _counting_scrape(monkeypatch, _fake_anime_info(anime_id), calls)

    await service.save_anime_controller(anime_id, user_id)

    assert len(calls) == 1
    assert await raw_conn.fetchval("SELECT count(*) FROM user_save_anime") == 1


async def test_update_dependency_rejects_placeholder_with_corrected_message(raw_conn):
    from exceptions import NotFoundError
    from packages.animes.dependencies import valid_anime_for_update

    await create_anime(raw_conn, anime_id="ph", title="Placeholder")

    with pytest.raises(NotFoundError) as exc:
        await valid_anime_for_update("ph", current_user={"id": "u"})

    assert "GET /animes/{anime_id}" in exc.value.message
    assert "/animes/info" not in exc.value.message


async def test_update_dependency_enforces_cooldown(raw_conn):
    from exceptions import TooManyRequestsError
    from packages.animes.dependencies import valid_anime_for_update

    await create_anime(
        raw_conn,
        anime_id="recent",
        title="T",
        last_scraped_at=datetime.now(timezone.utc) - timedelta(minutes=2),
    )

    with pytest.raises(TooManyRequestsError):
        await valid_anime_for_update("recent", current_user={"id": "u"})


async def test_update_dependency_allows_after_cooldown(raw_conn):
    from packages.animes.dependencies import valid_anime_for_update

    await create_anime(
        raw_conn,
        anime_id="old",
        title="T",
        last_scraped_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )

    data = await valid_anime_for_update("old", current_user={"id": "u"})

    assert data == {"anime_id": "old", "user_id": "u"}


# --- single-flight ----------------------------------------------------------


async def test_concurrent_syncs_share_one_scrape(raw_conn, monkeypatch):
    from packages.animes import service

    anime_id = "concurrent-anime"
    calls: list = []
    _counting_scrape(monkeypatch, _fake_anime_info(anime_id), calls, delay=0.2)

    await asyncio.gather(service.sync_anime(anime_id), service.sync_anime(anime_id))

    assert len(calls) == 1
    assert service._sync_inflight == {}


async def test_failed_sync_is_not_memoized(raw_conn, monkeypatch):
    from packages.animes import service

    anime_id = "failing-anime"
    calls: list = []
    _counting_scrape(monkeypatch, RuntimeError("fail"), calls, delay=0.1)

    results = await asyncio.gather(
        service.sync_anime(anime_id), service.sync_anime(anime_id), return_exceptions=True
    )
    assert all(isinstance(r, RuntimeError) for r in results)
    assert len(calls) == 1

    with pytest.raises(RuntimeError):
        await service.sync_anime(anime_id)
    assert len(calls) == 2


async def test_cancelled_waiter_does_not_cancel_shared_sync(raw_conn, monkeypatch):
    from packages.animes import service

    anime_id = "cancel-anime"
    calls: list = []
    _counting_scrape(monkeypatch, _fake_anime_info(anime_id), calls, delay=0.2)

    first = asyncio.create_task(service.sync_anime(anime_id))
    second = asyncio.create_task(service.sync_anime(anime_id))
    await asyncio.sleep(0.05)
    first.cancel()
    await second

    assert len(calls) == 1
    scraped_at = await raw_conn.fetchval(
        "SELECT last_scraped_at FROM animes WHERE id = $1", anime_id
    )
    assert scraped_at is not None


# --- response contract ------------------------------------------------------


async def test_detail_has_episode_url_and_no_platform(raw_conn):
    from packages.animes import service

    anime_id = "contract-anime"
    await create_anime(
        raw_conn,
        anime_id=anime_id,
        title="T",
        description="d",
        poster="p",
        type="TV",
        is_finished=False,
        last_scraped_at=datetime.now(timezone.utc),
    )
    await create_episode(
        raw_conn,
        anime_id=anime_id,
        ep_number=1,
        url="https://animeav1.com/media/contract-anime/1",
    )
    user_id = await create_user(raw_conn)

    result = await service.get_anime_controller(anime_id, user_id)
    dumped = result.model_dump(by_alias=True)

    assert "platform" not in dumped
    assert dumped["episodes"][0]["url"] == "https://animeav1.com/media/contract-anime/1"


# --- provider error translation (Phase 2) -----------------------------------


class _RaisingScraper:
    def __init__(self, exc):
        self.exc = exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def get_anime_info(self, **kwargs):
        raise self.exc

    async def search_anime(self, **kwargs):
        raise self.exc


@pytest.mark.parametrize(
    "exc, status",
    [
        (ScraperNotFoundError("nf", status_code=404), 404),
        (ScraperBlockedError("blocked", status_code=403), 429),
        (ScraperBlockedError("blocked"), 429),
        (ScraperHTTPError("5xx", status_code=503), 502),
        (ScraperHTTPError("conn failure"), 502),
        (ScraperTimeoutError("timeout"), 502),
        (ScraperParseError("no data"), 502),
    ],
)
async def test_scraper_errors_translate_to_http_status(monkeypatch, exc, status):
    from exceptions import AppError
    from packages.animes import scraper

    monkeypatch.setattr(scraper, "AnimeAV1Scraper", lambda: _RaisingScraper(exc))

    with pytest.raises(AppError) as info:
        await scraper.scrape_anime_info("some-anime")
    assert info.value.status_code == status

    with pytest.raises(AppError) as info:
        await scraper.scrape_search_anime("q")
    assert info.value.status_code == status


async def test_parse_error_is_502_and_anime_is_not_marked_scraped(raw_conn, monkeypatch):
    from exceptions import ExternalServiceError
    from packages.animes import scraper, service

    anime_id = "empty-page"
    monkeypatch.setattr(
        scraper, "AnimeAV1Scraper", lambda: _RaisingScraper(ScraperParseError("no data"))
    )
    user_id = await create_user(raw_conn)

    with pytest.raises(ExternalServiceError):
        await service.get_anime_controller(anime_id, user_id)

    assert await raw_conn.fetchval("SELECT count(*) FROM animes WHERE id = $1", anime_id) == 0
