import logging
import sys

from loguru import logger

# Loggers that spam full tracebacks for errors we already handle ourselves.
_NO_TRACEBACK = frozenset({
    "dramatiq.worker.WorkerThread",
    "dramatiq.middleware.retries.Retries",
    "asyncio",
})

# Loggers whose INFO/DEBUG output adds no value in production.
_QUIET = frozenset({"databases", "asyncpg", "dramatiq.worker.ForkingProcess"})


class _InterceptHandler(logging.Handler):
    """Bridge stdlib logging into loguru, stripping tracebacks from framework loggers."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        exc = None if record.name in _NO_TRACEBACK else record.exc_info
        logger.opt(exception=exc, depth=6).log(level, record.getMessage())


def configure_logs() -> None:
    logger_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "<level>{level: <5}</level> | "
        "{name}:{function}:{line} | "
        "{extra} | "
        "<level>{message}</level>"
    )

    logger.remove()
    logger.add(sys.stdout, level="DEBUG", format=logger_format)

    # Take over all stdlib logging and route through loguru.
    logging.basicConfig(handlers=[_InterceptHandler()], level=logging.DEBUG, force=True)

    for name in _QUIET:
        logging.getLogger(name).setLevel(logging.WARNING)
