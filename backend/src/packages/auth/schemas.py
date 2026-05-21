from pydantic import BaseModel


class LoginInfo(BaseModel):
    username: str
    password: str


class RegisterInfo(BaseModel):
    username: str
    password: str
