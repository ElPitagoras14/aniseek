from models import CamelCaseModel


class PasswordInfo(CamelCaseModel):
    current_password: str | None = None
    new_password: str | None = None


class UserUpdateInfo(CamelCaseModel):
    username: str | None = None
    password: PasswordInfo | None = None
    avatar_id: int | None = None
    role: str | None = None


class UserCreateInfo(CamelCaseModel):
    username: str
    password: str
    role: str = "member"


class UserAdminUpdateInfo(CamelCaseModel):
    is_active: bool | None = None
    role: str | None = None


class PasswordResetInfo(CamelCaseModel):
    password: str
