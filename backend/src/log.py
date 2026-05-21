import sys

from loguru import logger


def configure_logs(level="INFO"):
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
        level=level,
        format=logger_format,
    )
