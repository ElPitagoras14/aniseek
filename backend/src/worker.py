import dramatiq
from dramatiq.brokers.redis import RedisBroker
from config import general_settings
from loguru import logger

REDIS_URL = general_settings.REDIS_URL

broker = RedisBroker(url=REDIS_URL)
dramatiq.set_broker(broker)


@dramatiq.actor
def download_anime_episode(anime_id: str, episode_number: int, user_id: str):
    parsed_episode = str(episode_number).zfill(2)
    logger.info(f"Downloading {anime_id} E{parsed_episode}")


@dramatiq.actor
def order_franchise(franchise_info: dict):
    logger.info(f"Ordering franchise {franchise_info['id']}")
    pass
