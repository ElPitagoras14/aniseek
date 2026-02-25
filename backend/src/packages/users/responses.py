from datetime import datetime
from pydantic import BaseModel

from utils.models import CamelCaseModel


class User(CamelCaseModel):
    id: str
    username: str
    avatar_url: str | None = None
    avatar_label: str | None = None
    role: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserOut(BaseModel):
    payload: User | None


class UserList(BaseModel):
    items: list[User]
    total: int


class UserListOut(BaseModel):
    payload: UserList | None


class Avatar(BaseModel):
    id: int
    label: str
    url: str


class AvatarList(BaseModel):
    items: list[Avatar]
    total: int


class AvatarListOut(BaseModel):
    payload: AvatarList | None


class Statistics(CamelCaseModel):
    saved_animes: int
    downloaded_episodes: int
    in_emission_animes: int


class StatisticsOut(BaseModel):
    payload: Statistics | None
