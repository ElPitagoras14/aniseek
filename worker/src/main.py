import asyncio
from pathlib import Path

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import CurrentMessage
from loguru import logger

from config import general_settings
from log import configure_logs
from schemas import FranchiseInfo
from tasks import download_anime_episode_controller, order_franchise_controller

configure_logs()

Path(general_settings.ANIMES_FOLDER).mkdir(parents=True, exist_ok=True)

broker = RedisBroker(url=general_settings.REDIS_URL)
broker.add_middleware(CurrentMessage())
dramatiq.set_broker(broker)

logger.info("Dramatiq worker initialized")

_retries = general_settings.MAX_DOWNLOAD_RETRIES
_min_backoff = general_settings.RETRY_DOWNLOAD_INTERVAL * 1000


@dramatiq.actor(
    max_retries=_retries,
    min_backoff=_min_backoff,
    max_backoff=_min_backoff * (2 ** (_retries - 1)),
)
def download_anime_episode(anime_id: str, episode_number: int, user_id: str):
    message = CurrentMessage.get_current_message()
    # asyncio.run only because the controller drives async scrapers; everything
    # else (db, redis, file I/O) is sync and runs directly on the worker thread.
    asyncio.run(
        download_anime_episode_controller(message, anime_id, episode_number, user_id)
    )


@dramatiq.actor
def order_franchise(franchise_info: FranchiseInfo):
    order_franchise_controller(franchise_info)
