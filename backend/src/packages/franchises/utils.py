from .responses import (
    AnimeFranchise,
    AnimeFranchiseList,
    BaseAnime,
    Franchise,
    FranchiseList,
)
from utils.cast import create_caster


cast_base_anime = create_caster(BaseAnime)
cast_anime_franchise = create_caster(AnimeFranchise)


def cast_franchise(franchise: dict) -> Franchise:
    return Franchise(
        id=franchise["id"],
        name=franchise["name"],
        animes=[cast_base_anime(anime) for anime in franchise["animes"]],
    )


def cast_franchise_list(
    franchises: list[dict],
    total: int,
) -> FranchiseList:
    return FranchiseList(
        items=[cast_franchise(franchise) for franchise in franchises],
        total=total,
    )


def cast_anime_franchise_list(
    anime_franchises: list[dict],
) -> AnimeFranchiseList:
    return AnimeFranchiseList(
        items=[
            cast_anime_franchise(anime_franchise)
            for anime_franchise in anime_franchises
        ],
        total=len(anime_franchises),
    )
