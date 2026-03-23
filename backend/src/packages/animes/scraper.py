from urllib.parse import urlparse

from ani_scrapy import AnimeAV1Scraper
from ani_scrapy.core import AnimeInfo, EpisodeInfo, PagedSearchAnimeInfo

from loguru import logger

from .config import anime_settings


def _normalize_anime_id(anime_id: str) -> str:
    if anime_id.startswith(("http://", "https://")):
        parsed = urlparse(anime_id)
        path = parsed.path.rstrip("/")
        # Get last non-empty segment
        slug = path.split("/")[-1]
        return slug
    return anime_id


async def scrape_anime_info(
    anime_id: str,
    include_episodes: bool = True,
) -> AnimeInfo:
    anime_id = _normalize_anime_id(anime_id)
    logger.debug(f"Scraping anime info: {anime_id}")

    async with AnimeAV1Scraper(executable_path=anime_settings.BRAVE_PATH) as scraper:
        return await scraper.get_anime_info(
            anime_id=anime_id,
            include_episodes=include_episodes,
        )


async def scrape_new_episodes(
    anime_id: str,
    last_episode_number: int,
) -> list[EpisodeInfo]:
    anime_id = _normalize_anime_id(anime_id)
    logger.debug(
        f"Scraping new episodes: {anime_id} after {last_episode_number}"
    )

    async with AnimeAV1Scraper(executable_path=anime_settings.BRAVE_PATH) as scraper:
        return await scraper.get_new_episodes(
            anime_id=anime_id,
            last_episode_number=last_episode_number,
        )


async def scrape_search_anime(
    query: str,
) -> PagedSearchAnimeInfo:
    logger.debug(f"Searching anime: {query}")

    async with AnimeAV1Scraper(executable_path=anime_settings.BRAVE_PATH) as scraper:
        return await scraper.search_anime(
            query=query,
        )
