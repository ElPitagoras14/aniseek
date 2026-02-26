import asyncio
import dramatiq

from pathlib import Path
from log import configure_logs
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import CurrentMessage
from loguru import logger

from config import general_settings
from schemas import FranchiseInfo
from tasks import download_anime_episode_controller, order_franchise_controller

REDIS_URL = general_settings.REDIS_URL
MAX_DOWNLOAD_RETRIES = general_settings.MAX_DOWNLOAD_RETRIES
RETRY_DOWNLOAD_INTERVAL = general_settings.RETRY_DOWNLOAD_INTERVAL
ANIMES_FOLDER = general_settings.ANIMES_FOLDER

configure_logs()

Path(ANIMES_FOLDER).mkdir(parents=True, exist_ok=True)

broker = RedisBroker(url=REDIS_URL)
broker.add_middleware(CurrentMessage())
dramatiq.set_broker(broker)

logger.info("Dramatiq worker initialized")


@dramatiq.actor(
    max_retries=MAX_DOWNLOAD_RETRIES,
    min_backoff=RETRY_DOWNLOAD_INTERVAL * 1000,
    max_backoff=RETRY_DOWNLOAD_INTERVAL * 1000 * MAX_DOWNLOAD_RETRIES * 2,
)
def download_anime_episode(anime_id: str, episode_number: int, user_id: str):
    message = CurrentMessage.get_current_message()

    asyncio.run(
        download_anime_episode_controller(
            message,
            anime_id,
            episode_number,
            user_id,
        )
    )


@dramatiq.actor
def order_franchise(franchise_info: FranchiseInfo):
    order_franchise_controller(franchise_info)
