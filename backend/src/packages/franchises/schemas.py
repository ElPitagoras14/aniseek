from pydantic import BaseModel


class AnimeInfo(BaseModel):
    id: str
    season: int


class FranchiseCreate(BaseModel):
    franchise: str
    animes: list[AnimeInfo]
