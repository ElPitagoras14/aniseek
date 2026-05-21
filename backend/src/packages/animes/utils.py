from utils.cast import create_caster

from .responses import (
    Anime,
    EpisodeInfo,
    InEmissionAnime,
    InEmissionAnimeList,
    RelatedInfo,
    SearchAnimeResult,
    SearchAnimeResultList,
)

cast_search_anime_result = create_caster(SearchAnimeResult)
cast_in_emission_anime = create_caster(InEmissionAnime)


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
            RelatedInfo(id=related["id"], title=related["title"], type=related["type"])
            for related in anime["related_info"]
        ],
        week_day=anime["week_day"],
        is_finished=anime["is_finished"],
        last_scraped_at=anime["last_scraped_at"],
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
