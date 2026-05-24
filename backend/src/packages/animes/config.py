from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnimeSettings(BaseSettings):
    REDIS_URL: str

    ANIMES_FOLDER: str

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env", usecwd=True),
        env_file_encoding="utf-8",
        extra="ignore",
    )


anime_settings = AnimeSettings()
