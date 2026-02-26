import sys
from loguru import logger

from config import general_settings

APP_LOG_PATH = general_settings.APP_LOG_PATH
ERROR_PATH = general_settings.ERROR_PATH


def configure_logs():
    logger_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level> | {extra}"
    )

    logger.remove()
    logger.add(sys.stderr, format=logger_format)
    logger.remove()

    logger.add(
        sys.stdout,
        level="DEBUG",
        format=logger_format,
    )

    if APP_LOG_PATH:
        logger.add(
            APP_LOG_PATH,
            rotation="10 MB",
            retention="30 days",
            level="INFO",
            format=logger_format,
        )
