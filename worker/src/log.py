import sys
from loguru import logger


def configure_logs():
    logger_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "<level>{level: <5}</level> | "
        "{name}:{function}:{line} | "
        "<level>{message}</level>"
    )

    logger.remove()
    logger.add(
        sys.stdout,
        level="DEBUG",
        format=logger_format,
    )
