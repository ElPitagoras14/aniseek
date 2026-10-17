from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXP_MIN: int
    REFRESH_TOKEN_EXP_DAY: float
    AUTH_ENABLED: bool = True
    # Only used to create the owner on a fresh install (see owner.ensure_owner).
    OWNER_USERNAME: str | None = None
    OWNER_PASSWORD: str | None = None

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env", usecwd=True),
        env_file_encoding="utf-8",
        extra="ignore",
    )


auth_settings = AuthSettings()
