from .responses import (
    AnimeDownloadInfo,
    AnimeDownloadInfoList,
    AnimeStorageInfo,
    AnimeStorageInfoList,
    DownloadTaskList,
    DownloadTaskStatus,
    EpisodeDownload,
    EpisodeDownloadList,
    SearchAnimeResult,
    SearchAnimeResultList,
    Anime,
    InEmissionAnime,
    InEmissionAnimeList,
    EpisodeInfo,
    RelatedInfo,
    DownloadTask,
)
from utils.cast import create_caster


cast_search_anime_result = create_caster(SearchAnimeResult)
cast_in_emission_anime = create_caster(InEmissionAnime)
cast_episode_download = create_caster(EpisodeDownload)
cast_download_task = create_caster(DownloadTaskStatus)
cast_anime_download_info = create_caster(AnimeDownloadInfo)
cast_anime_storage = create_caster(AnimeStorageInfo)


def cast_job_id(job_id: str) -> DownloadTask:
    return DownloadTask(job_id=job_id)


def cast_anime_info(anime: dict, saved: dict) -> Anime:
    return Anime(
        id=anime["id"],
        title=anime["title"],
        type=anime["type"],
        poster=anime["poster"],
        is_saved=saved["is_saved"],
        save_date=saved["save_date"],
        season=1,
        other_titles=[title for title in anime["other_titles"]],
        platform="JKAnime",
        description=anime["description"],
        genres=anime["genres"],
        related_info=[
            RelatedInfo(
                id=related["id"], title=related["title"], type=related["type"]
            )
            for related in anime["related_info"]
        ],
        week_day=anime["week_day"],
        is_finished=anime["is_finished"],
        last_scraped_at=anime["last_scraped_at"],
        last_forced_update=anime["last_forced_update"],
        episodes=[
            EpisodeInfo(
                id=episode["id"],
                anime_id=episode["anime_id"],
                image_preview=episode["image_preview"],
                is_user_downloaded=episode["is_user_downloaded"],
                is_global_downloaded=episode["is_global_downloaded"],
            )
            for episode in anime["episodes"]
        ],
    )


def cast_search_anime_result_list(
    animes: list[dict],
) -> SearchAnimeResultList:
    return SearchAnimeResultList(
        items=[cast_search_anime_result(anime) for anime in animes],
        total=len(animes),
    )


def cast_in_emission_anime_list(
    animes: list[dict],
) -> InEmissionAnimeList:
    return InEmissionAnimeList(
        items=[cast_in_emission_anime(anime) for anime in animes],
        total=len(animes),
    )


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
        items=[
            cast_download_task(download_task)
            for download_task in download_tasks
        ],
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
