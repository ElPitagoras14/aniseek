from .responses import (
    AnimeFranchise,
    AnimeFranchiseList,
    BaseAnime,
    Franchise,
    FranchiseList,
)


def cast_franchise(franchise: dict) -> Franchise:
    return Franchise(
        id=franchise["id"],
        name=franchise["name"],
        animes=[BaseAnime(**a) for a in franchise["animes"]],
    )


def cast_franchise_list(franchises: list[dict], total: int) -> FranchiseList:
    return FranchiseList(
        items=[cast_franchise(f) for f in franchises],
        total=total,
    )


def cast_anime_franchise_list(anime_franchises: list[dict]) -> AnimeFranchiseList:
    return AnimeFranchiseList(
        items=[AnimeFranchise(**af) for af in anime_franchises],
        total=len(anime_franchises),
    )
