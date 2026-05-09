import logging
import sys

from loguru import logger
from src.core.config import Settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def configure_logging(settings: Settings) -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level="DEBUG" if settings.debug else "INFO",
        enqueue=True,
        backtrace=settings.debug,
        diagnose=settings.debug,
        serialize=settings.environment == "production",
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
