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


def cast_job_id(job_id: str) -> DownloadTask:
    return DownloadTask(job_id=job_id)


def cast_episode_download_list(
    episode_downloads: list[dict], total: int
) -> EpisodeDownloadList:
    return EpisodeDownloadList(
        items=[EpisodeDownload(**ed) for ed in episode_downloads],
        total=total,
    )


def cast_download_task_list(download_tasks: list[dict], total: int) -> DownloadTaskList:
    return DownloadTaskList(
        items=[DownloadTaskStatus(**dt) for dt in download_tasks],
        total=total,
    )


def cast_downloaded_anime_list(animes: list[dict], total: int) -> AnimeDownloadInfoList:
    return AnimeDownloadInfoList(
        items=[AnimeDownloadInfo(**a) for a in animes],
        total=total,
    )


def cast_animes_storage_list(
    animes: list[dict], total: int, total_size: int = 0
) -> AnimeStorageInfoList:
    return AnimeStorageInfoList(
        items=[AnimeStorageInfo(**a) for a in animes],
        total=total,
        total_size=total_size,
    )
