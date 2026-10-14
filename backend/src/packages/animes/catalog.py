"""Catalog provider (AnimeAV1): the only place the backend knows its URLs."""

PROVIDER_BASE_URL = "https://animeav1.com"


def media_url(anime_id: str) -> str:
    return f"{PROVIDER_BASE_URL}/media/{anime_id}"


def episode_url(anime_id: str, episode_number: int) -> str:
    return f"{media_url(anime_id)}/{episode_number}"
