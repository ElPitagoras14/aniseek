from pydantic import BaseModel

from models import CamelCaseModel


class LoginInfo(BaseModel):
    username: str
    password: str


class RegisterInfo(CamelCaseModel):
    username: str
    password: str
    invitation_token: str | None = None
