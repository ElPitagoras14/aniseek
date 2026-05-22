from .responses import (
    Anime,
    EpisodeInfo,
    InEmissionAnime,
    InEmissionAnimeList,
    RelatedInfo,
    SavedAnimeResult,
    SavedAnimeResultList,
    SearchAnimeResult,
    SearchAnimeResultList,
)


def cast_anime_info(anime: dict, saved: dict) -> Anime:
    return Anime(
        id=anime["id"],
        title=anime["title"],
        type=anime["type"],
        poster=anime["poster"],
        is_saved=saved["is_saved"],
        save_date=saved["save_date"],
        season=1,
        platform="AnimeAV1",
        description=anime["description"],
        genres=anime["genres"],
        related_info=[
            RelatedInfo(id=r["id"], title=r["title"], type=r["type"])
            for r in anime["related_info"]
        ],
        week_day=anime["week_day"],
        is_finished=anime["is_finished"],
        last_scraped_at=anime["last_scraped_at"],
        episodes=[
            EpisodeInfo(
                id=ep["id"],
                anime_id=ep["anime_id"],
                image_preview=ep["image_preview"],
                is_user_downloaded=ep["is_user_downloaded"],
                is_global_downloaded=ep["is_global_downloaded"],
            )
            for ep in anime["episodes"]
        ],
    )


def cast_search_anime_result_list(animes: list[dict]) -> SearchAnimeResultList:
    return SearchAnimeResultList(
        items=[SearchAnimeResult(**a) for a in animes],
        total=len(animes),
    )


def cast_in_emission_anime_list(animes: list[dict]) -> InEmissionAnimeList:
    return InEmissionAnimeList(
        items=[InEmissionAnime(**a) for a in animes],
        total=len(animes),
    )


def cast_saved_anime_result_list(animes: list[dict]) -> SavedAnimeResultList:
    return SavedAnimeResultList(
        items=[SavedAnimeResult(**a) for a in animes],
        total=len(animes),
    )
