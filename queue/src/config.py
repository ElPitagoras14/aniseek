from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneralSettings(BaseSettings):
    REDIS_URL: str

    MAX_DOWNLOAD_RETRIES: int
    RETRY_DOWNLOAD_INTERVAL: int
    ANIMES_FOLDER: str
    WORKER_LOG_PATH: str | None = None

    BRAVE_PATH: str | None = None

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env", usecwd=True),
        env_file_encoding="utf-8",
        extra="ignore",
    )


general_settings = GeneralSettings()
