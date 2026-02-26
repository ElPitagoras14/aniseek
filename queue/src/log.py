import sys
from loguru import logger

from config import general_settings

WORKER_LOG_PATH = general_settings.WORKER_LOG_PATH


def configure_logs():
    logger_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "<level>{level: <5}</level> | "
        "{name}:{function}:{line} | "
        "<level>{message}</level>"
    )

    logger.remove(0)
    logger.add(
        sys.stdout,
        level="DEBUG",
        format=logger_format,
    )

    if WORKER_LOG_PATH:
        logger.add(
            WORKER_LOG_PATH,
            rotation="10 MB",
            retention="30 days",
            level="INFO",
            format=logger_format,
            enqueue=True,
        )
