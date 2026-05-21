from utils.cast import create_caster

from .responses import (
    AnimeDownloadInfo,
    AnimeDownloadInfoList,
    AnimeStorageInfo,
    AnimeStorageInfoList,
    DownloadTask,
    DownloadTaskList,
    DownloadTaskStatus,
    EpisodeDownload,
    EpisodeDownloadList,
)

cast_episode_download = create_caster(EpisodeDownload)
cast_download_task = create_caster(DownloadTaskStatus)
cast_anime_download_info = create_caster(AnimeDownloadInfo)
cast_anime_storage = create_caster(AnimeStorageInfo)


def cast_job_id(job_id: str) -> DownloadTask:
    return DownloadTask(job_id=job_id)


def cast_episode_download_list(
    episode_downloads: list[dict],
    total: int,
) -> EpisodeDownloadList:
    return EpisodeDownloadList(
        items=[
            cast_episode_download(episode_download)
            for episode_download in episode_downloads
        ],
        total=total,
    )


def cast_download_task_list(
    download_tasks: list[dict],
    total: int,
) -> DownloadTaskList:
    return DownloadTaskList(
        items=[cast_download_task(download_task) for download_task in download_tasks],
        total=total,
    )


def cast_downloaded_anime_list(
    animes: list[dict],
    total: int,
) -> AnimeDownloadInfoList:
    return AnimeDownloadInfoList(
        items=[cast_anime_download_info(anime) for anime in animes],
        total=total,
    )


def cast_animes_storage_list(
    animes: list[dict],
    total: int,
) -> AnimeStorageInfoList:
    return AnimeStorageInfoList(
        items=[cast_anime_storage(anime) for anime in animes],
        total=total,
    )
