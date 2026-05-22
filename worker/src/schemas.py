from typing import TypedDict


class AnimeInfo(TypedDict):
    id: str
    season: int


class FranchiseInfo(TypedDict):
    id: str
    name: str
    animes: list[AnimeInfo]
