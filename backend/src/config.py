from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneralSettings(BaseSettings):
    ADMIN_USER: str
    ADMIN_PASS: str

    APP_LOG_PATH: str | None = None
    ERROR_PATH: str | None = None

    SECRET_KEY: str
    ALGORITHM: str

    REDIS_URL: str

    ENVIRONMENT: str = "local"

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env", usecwd=True),
        env_file_encoding="utf-8",
        extra="ignore",
    )


general_settings = GeneralSettings()
