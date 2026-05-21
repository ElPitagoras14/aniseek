from pydantic import BaseModel

from responses import SuccessResponse


class Tokens(BaseModel):
    access: str
    refresh: str


class TokenOut(SuccessResponse):
    payload: Tokens | None


class AccessToken(BaseModel):
    access: str


class AccessTokenOut(SuccessResponse):
    payload: AccessToken | None
