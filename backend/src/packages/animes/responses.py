from datetime import datetime

from pydantic import BaseModel

from models import CamelCaseModel
from responses import SuccessResponse


class RelatedInfo(BaseModel):
    id: str
    title: str
    type: str


class EpisodeInfo(CamelCaseModel):
    id: int
    anime_id: str
    image_preview: str | None = None
    is_user_downloaded: bool
    is_global_downloaded: bool


class BaseAnime(CamelCaseModel):
    id: str
    title: str
    type: str
    poster: str
    is_saved: bool
    save_date: datetime | None = None


class SearchAnimeResult(BaseAnime):
    pass


class SearchAnimeResultList(BaseModel):
    items: list[SearchAnimeResult]
    total: int


class SearchAnimeResultListOut(SuccessResponse):
    payload: SearchAnimeResultList | None


class Anime(BaseAnime):
    season: int | None = None
    platform: str
    description: str
    genres: list[str]
    related_info: list[RelatedInfo]
    week_day: str | None = None
    episodes: list[EpisodeInfo]
    is_finished: bool
    last_scraped_at: datetime | None = None


class AnimeOut(SuccessResponse):
    payload: Anime | None


class InEmissionAnime(BaseAnime):
    week_day: str


class InEmissionAnimeList(BaseModel):
    items: list[InEmissionAnime]
    total: int


class InEmissionAnimeListOut(SuccessResponse):
    payload: InEmissionAnimeList | None


class SavedAnimeResult(BaseAnime):
    is_finished: bool


class SavedAnimeResultList(BaseModel):
    items: list[SavedAnimeResult]
    total: int


class SavedAnimeResultListOut(SuccessResponse):
    payload: SavedAnimeResultList | None
