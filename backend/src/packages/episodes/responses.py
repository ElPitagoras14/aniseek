from datetime import datetime

from pydantic import BaseModel

from models import CamelCaseModel
from responses import SuccessResponse


class EpisodeDownload(CamelCaseModel):
    id: int
    anime_id: str
    title: str
    episode_number: int
    poster: str
    job_id: str | None = None
    size: int | None = None
    status: str
    downloaded_at: datetime | None = None


class EpisodeDownloadList(BaseModel):
    items: list[EpisodeDownload]
    total: int


class EpisodeDownloadListOut(SuccessResponse):
    payload: EpisodeDownloadList | None


class AnimeDownloadInfo(BaseModel):
    id: str
    title: str


class AnimeDownloadInfoList(BaseModel):
    items: list[AnimeDownloadInfo]
    total: int


class AnimeDownloadInfoListOut(SuccessResponse):
    payload: AnimeDownloadInfoList | None


class DownloadTask(BaseModel):
    job_id: str | None = None


class DownloadTaskOut(SuccessResponse):
    payload: DownloadTask | None


class DownloadTaskStatus(DownloadTask):
    episode_number: int
    success: bool


class DownloadTaskList(BaseModel):
    items: list[DownloadTaskStatus]
    total: int


class DownloadTaskListOut(SuccessResponse):
    payload: DownloadTaskList | None


class AnimeStorageInfo(BaseModel):
    id: str
    title: str
    size: int


class AnimeStorageInfoList(CamelCaseModel):
    items: list[AnimeStorageInfo]
    total: int
    total_size: int = 0


class AnimeStorageInfoListOut(SuccessResponse):
    payload: AnimeStorageInfoList | None
