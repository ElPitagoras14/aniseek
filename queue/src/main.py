import os
import asyncio
import sys
from celery import Celery
from celery.signals import worker_ready
from loguru import logger

from tasks import download_anime_episode_controller, order_franchise_controller
from config import general_settings
from schemas import FranchiseInfo

if sys.platform == "win32":
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)


REDIS_URL = general_settings.REDIS_URL
MAX_DOWNLOAD_RETRIES = general_settings.MAX_DOWNLOAD_RETRIES
RETRY_DOWNLOAD_INTERVAL = general_settings.RETRY_DOWNLOAD_INTERVAL
ANIMES_FOLDER = general_settings.ANIMES_FOLDER

os.makedirs(ANIMES_FOLDER, exist_ok=True)


celery_app = Celery(
    "queues",
    broker=f"{REDIS_URL}/0",
    backend=f"{REDIS_URL}/1",
)

celery_app.conf.update(
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    result_backend=f"{REDIS_URL}/1",
    worker_pool="threads",
    worker_concurrency=5,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
)


@worker_ready.connect
def on_worker_ready(**kwargs):
    logger.info("Celery workers are ready")


@celery_app.task(
    name="tasks.download_anime_episode",
    bind=True,
    max_retries=MAX_DOWNLOAD_RETRIES,
    default_retry_delay=RETRY_DOWNLOAD_INTERVAL,
)
def download_anime_episode(
    self,
    anime_id: str,
    episode_number: int,
    user_id: str,
):
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    download_anime_episode_controller(
        self,
        anime_id,
        episode_number,
        user_id,
    )


@celery_app.task(name="tasks.order_franchise")
def order_franchise(franchise_info: FranchiseInfo):
    order_franchise_controller(franchise_info)


if __name__ == "__main__":
    args = ["worker", "--loglevel=info"]
    celery_app.worker_main(argv=args)
