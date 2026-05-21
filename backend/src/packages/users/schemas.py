from models import CamelCaseModel


class PasswordInfo(CamelCaseModel):
    current_password: str | None = None
    new_password: str | None = None


class UserUpdateInfo(CamelCaseModel):
    username: str | None = None
    password: PasswordInfo | None = None
    avatar_id: int | None = None
    role: str | None = None
