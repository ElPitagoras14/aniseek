"""decouple-anime-scrape-persist: covers the two things that change in
packages/animes/service.py:

- The pure mapping helpers (_anime_fields_from_info, _episode_values)
  extracted out of add_new_anime/update_anime_info — no I/O, so no database
  or scraping fixtures needed.
- That update_anime_info actually performs both scrapes (and the rate-limit
  sleep between them) before it opens its write transaction, not just after
  the reorder "looks right" in the diff.
"""

from datetime import datetime, timezone

from ani_scrapy.core import AnimeType, EpisodeInfo
from factories import create_anime

from test_animes_atomicity import _fake_anime_info, _no_sleep


def test_anime_fields_from_info_maps_columns_without_week_day():
    from packages.animes.service import _anime_fields_from_info

    info = _fake_anime_info("anime-1", type=AnimeType.TV, next_episode_date=None)
    current_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    fields = _anime_fields_from_info(info, current_time)

    assert fields == {
        "title": info.title,
        "description": info.description,
        "poster": info.poster,
        "type": "TV",
        "is_finished": info.is_finished,
        "week_day": None,
        "last_scraped_at": current_time,
    }


def test_anime_fields_from_info_derives_week_day_from_next_episode_date():
    from packages.animes.service import _anime_fields_from_info

    # 2026-01-05 is a Monday.
    next_episode = datetime(2026, 1, 5, tzinfo=timezone.utc)
    info = _fake_anime_info("anime-1", next_episode_date=next_episode)

    fields = _anime_fields_from_info(info, datetime.now(timezone.utc))

    assert fields["week_day"] == "Monday"


def test_episode_values_maps_episodes_to_insertable_rows():
    from packages.animes.service import _episode_values

    episodes = [
        EpisodeInfo(episode_number=1, anime_id="anime-1", image_preview="preview-1.png"),
        EpisodeInfo(episode_number=2, anime_id="anime-1", image_preview=None),
    ]

    values = _episode_values(episodes, "anime-1", "https://example.test/media/anime-1")

    assert values == [
        {
            "anime_id": "anime-1",
            "ep_number": 1,
            "preview": "preview-1.png",
            "url": "https://example.test/media/anime-1/1",
        },
        {
            "anime_id": "anime-1",
            "ep_number": 2,
            "preview": None,
            "url": "https://example.test/media/anime-1/2",
        },
    ]


def test_episode_values_of_empty_list_is_empty():
    from packages.animes.service import _episode_values

    assert _episode_values([], "anime-1", "https://example.test") == []


async def test_update_anime_info_scrapes_before_opening_write_transaction(
    raw_conn, monkeypatch
):
    import asyncio

    from packages.animes import repository, service

    anime_id = "order-update-anime"
    await create_anime(raw_conn, anime_id=anime_id, title="Previous Title")

    call_order = []

    def _tracking_scrape(name, result):
        async def _scrape(*args, **kwargs):
            call_order.append(name)
            return result

        return _scrape

    fake_info = _fake_anime_info(anime_id, related_info=[])
    monkeypatch.setattr(
        service, "scrape_anime_info", _tracking_scrape("scrape_anime_info", fake_info)
    )
    monkeypatch.setattr(
        service, "scrape_new_episodes", _tracking_scrape("scrape_new_episodes", [])
    )
    monkeypatch.setattr(asyncio, "sleep", _no_sleep)

    original_update_anime_fields = repository.update_anime_fields

    async def _tracking_update_anime_fields(conn, anime_id, values):
        # The first write inside update_anime_info's transaction: reaching it
        # proves the write transaction has opened by this point.
        call_order.append("update_anime_fields")
        return await original_update_anime_fields(conn, anime_id, values)

    monkeypatch.setattr(repository, "update_anime_fields", _tracking_update_anime_fields)

    await service.update_anime_info("https://example.test", anime_id)

    assert call_order == ["scrape_anime_info", "scrape_new_episodes", "update_anime_fields"]
