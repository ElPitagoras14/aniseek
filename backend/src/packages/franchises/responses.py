from pydantic import BaseModel

from packages.animes.responses import BaseAnime
from utils.responses import SuccessResponse


class Franchise(BaseModel):
    id: str
    name: str
    animes: list[BaseAnime] | None


class FranchiseList(BaseModel):
    items: list[Franchise]
    total: int


class FranchiseListOut(SuccessResponse):
    payload: FranchiseList | None


class AnimeFranchise(BaseAnime):
    franchise: str | None


class AnimeFranchiseList(BaseModel):
    items: list[AnimeFranchise]
    total: int


class AnimeFranchiseListOut(SuccessResponse):
    payload: AnimeFranchiseList | None
