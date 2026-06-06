from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


ADMIN_USER = "admin"
ADMIN_PASS = "admin123"


class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXP_MIN: int
    REFRESH_TOKEN_EXP_DAY: float
    AUTH_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env", usecwd=True),
        env_file_encoding="utf-8",
        extra="ignore",
    )


auth_settings = AuthSettings()
