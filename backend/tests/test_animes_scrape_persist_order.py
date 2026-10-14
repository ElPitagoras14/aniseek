"""Pure mapping helpers of packages/animes (no I/O) and the ordering of the
single sync flow: the scrape happens exactly once and before the write
transaction opens."""

from datetime import datetime, timezone
from types import SimpleNamespace

from ani_scrapy.core import AnimeType, EpisodeInfo, RelatedInfo, RelatedType
from factories import create_anime

from test_animes_atomicity import _fake_anime_info


def test_episode_url_follows_provider_format():
    from packages.animes.catalog import episode_url, media_url

    assert episode_url("x", 3) == "https://animeav1.com/media/x/3"
    assert media_url("x") == "https://animeav1.com/media/x"


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

    values = _episode_values(episodes, "anime-1")

    assert values == [
        {
            "anime_id": "anime-1",
            "ep_number": 1,
            "preview": "preview-1.png",
            "url": "https://animeav1.com/media/anime-1/1",
        },
        {
            "anime_id": "anime-1",
            "ep_number": 2,
            "preview": None,
            "url": "https://animeav1.com/media/anime-1/2",
        },
    ]


def test_episode_values_of_empty_list_is_empty():
    from packages.animes.service import _episode_values

    assert _episode_values([], "anime-1") == []


def test_relation_rows_maps_known_types_and_skips_unknown_ones():
    from packages.animes.service import _relation_rows

    info = SimpleNamespace(
        id="anime-1",
        related_info=[
            RelatedInfo(id="seq", title="Sequel T", type=RelatedType.SEQUEL),
            SimpleNamespace(id="odd", title="Odd", type=SimpleNamespace(value="Spin-off")),
        ],
    )

    placeholders, relations = _relation_rows(info)

    assert placeholders == [{"id": "seq", "title": "Sequel T"}]
    assert relations == [
        {"anime_id": "anime-1", "related_anime_id": "seq", "type_related_id": 2}
    ]


async def test_sync_scrapes_once_before_opening_write_transaction(raw_conn, monkeypatch):
    from packages.animes import repository, service

    anime_id = "order-update-anime"
    await create_anime(raw_conn, anime_id=anime_id, title="Previous Title")

    call_order = []
    scrape_calls = []
    fake_info = _fake_anime_info(anime_id, related_info=[])

    async def _tracking_scrape(*args, **kwargs):
        scrape_calls.append((args, kwargs))
        call_order.append("scrape_anime_info")
        return fake_info

    monkeypatch.setattr(service, "scrape_anime_info", _tracking_scrape)

    original = repository.upsert_scraped_anime

    async def _tracking_upsert(conn, values):
        # First write inside the transaction: reaching it proves the write
        # transaction has opened by this point.
        call_order.append("upsert_scraped_anime")
        return await original(conn, values)

    monkeypatch.setattr(repository, "upsert_scraped_anime", _tracking_upsert)

    await service.sync_anime(anime_id)

    assert len(scrape_calls) == 1
    assert scrape_calls[0][1].get("include_episodes", True) is True
    assert call_order == ["scrape_anime_info", "upsert_scraped_anime"]
