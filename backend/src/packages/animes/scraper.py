from urllib.parse import urlparse

from ani_scrapy import AnimeAV1Scraper
from ani_scrapy.core import (
    AnimeInfo,
    PagedSearchAnimeInfo,
    ScraperBlockedError,
    ScraperError,
    ScraperNotFoundError,
)
from loguru import logger

from exceptions import ExternalServiceError, NotFoundError, TooManyRequestsError


def _normalize_anime_id(anime_id: str) -> str:
    if anime_id.startswith(("http://", "https://")):
        parsed = urlparse(anime_id)
        path = parsed.path.rstrip("/")
        # Extract the last non-empty path segment as the anime slug
        slug = path.split("/")[-1]
        return slug
    return anime_id


def _translate_scraper_error(exc: ScraperError) -> Exception:
    """Maps ani-scrapy errors to API errors. `status_code` may be None."""
    status = getattr(exc, "status_code", None)
    logger.warning(f"Provider error {type(exc).__name__} (status={status}): {exc}")
    if isinstance(exc, ScraperNotFoundError):
        return NotFoundError("Anime not found in the catalog provider")
    if isinstance(exc, ScraperBlockedError):
        return TooManyRequestsError("The catalog provider is blocking requests")
    return ExternalServiceError("The catalog provider failed to respond correctly")


async def scrape_anime_info(
    anime_id: str,
    include_episodes: bool = True,
) -> AnimeInfo:
    anime_id = _normalize_anime_id(anime_id)
    logger.debug(f"Scraping anime info: {anime_id}")

    try:
        async with AnimeAV1Scraper() as scraper:
            return await scraper.get_anime_info(
                anime_id=anime_id,
                include_episodes=include_episodes,
            )
    except ScraperError as exc:
        raise _translate_scraper_error(exc) from exc


async def scrape_search_anime(
    query: str,
) -> PagedSearchAnimeInfo:
    logger.debug(f"Searching anime: {query}")

    try:
        async with AnimeAV1Scraper() as scraper:
            return await scraper.search_anime(
                query=query,
            )
    except ScraperError as exc:
        raise _translate_scraper_error(exc) from exc
