"""Output models of the MCP tools (mcp-server, design D6). Built from the
services' data with `format_anime_id`, so every anime id leaves with its
provider. None of them carries a URL to download an episode file."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

EpisodeStatus = Literal[
    "not_downloaded",
    "pending",
    "getting_link",
    "downloading",
    "retrying",
    "downloaded",
    "failed",
]

_STATUS_BY_DB_VALUE: dict[str | None, EpisodeStatus] = {
    None: "not_downloaded",
    "PENDING": "pending",
    "GETTING-LINK": "getting_link",
    "DOWNLOADING": "downloading",
    "RETRYING": "retrying",
    "SUCCESS": "downloaded",
    "FAILED": "failed",
}


def episode_status(db_value: str | None) -> EpisodeStatus:
    return _STATUS_BY_DB_VALUE.get(db_value, "not_downloaded")


class AnimeSummary(BaseModel):
    id: str = Field(description="Provider-namespaced id, e.g. 'animeav1:one-piece'")
    title: str
    type: str | None = None
    is_saved: bool


class AnimeSearchResult(BaseModel):
    items: list[AnimeSummary]
    total: int


class RelatedAnime(BaseModel):
    id: str
    title: str | None = None
    relation: str


class EpisodeState(BaseModel):
    number: int
    status: EpisodeStatus
    requested_by_user: bool


class AnimeDetail(BaseModel):
    id: str
    title: str | None = None
    type: str | None = None
    description: str | None = None
    genres: list[str]
    is_finished: bool | None = None
    week_day: str | None = Field(None, description="Weekday a new episode airs")
    is_saved: bool
    saved_at: datetime | None = None
    last_synced_at: datetime | None = None
    related: list[RelatedAnime]
    episodes: list[EpisodeState]


class SavedAnime(BaseModel):
    id: str
    title: str
    type: str | None = None
    is_finished: bool | None = None
    saved_at: datetime | None = None


class SavedAnimeList(BaseModel):
    items: list[SavedAnime]
    total: int


class AiringAnime(BaseModel):
    id: str
    title: str
    week_day: str


class AiringAnimeList(BaseModel):
    items: list[AiringAnime]
    total: int


class DownloadRecord(BaseModel):
    anime_id: str
    anime_title: str
    episode_number: int
    status: EpisodeStatus
    size_bytes: int | None = None
    requested_at: datetime | None = None


class DownloadRecordList(BaseModel):
    items: list[DownloadRecord]
    total: int
    page: int


class AnimeStorage(BaseModel):
    anime_id: str
    title: str
    size_bytes: int


class StorageUsage(BaseModel):
    items: list[AnimeStorage]
    total: int
    total_size_bytes: int
    page: int


class UserStats(BaseModel):
    saved_animes: int
    downloaded_episodes: int
    airing_saved_animes: int


class SavedState(BaseModel):
    anime_id: str
    is_saved: bool


EpisodeRequestState = Literal[
    "enqueued", "already_downloaded", "not_found", "enqueue_failed"
]


class EpisodeRequestResult(BaseModel):
    number: int
    state: EpisodeRequestState


class DownloadRequestResult(BaseModel):
    anime_id: str
    episodes: list[EpisodeRequestResult]
    enqueued: int


class EpisodeDownloadStatus(BaseModel):
    number: int
    status: EpisodeStatus | Literal["not_found"]
    requested_by_user: bool


class DownloadStatusResult(BaseModel):
    anime_id: str
    episodes: list[EpisodeDownloadStatus]


class FilesDeleted(BaseModel):
    anime_id: str
    deleted: bool
