import logging
import sys

from loguru import logger

from src.nucleo.configuracao import Configuracoes


class CapturaLog(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            nivel: str | int = logger.level(record.levelname).name
        except ValueError:
            nivel = record.levelno

        logger.opt(depth=6, exception=record.exc_info).log(nivel, record.getMessage())


def configurar_logs(config: Configuracoes) -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level="DEBUG" if config.depurar else "INFO",
        enqueue=True,
        backtrace=config.depurar,
        diagnose=config.depurar,
        serialize=config.ambiente == "production",
    )
    logging.basicConfig(handlers=[CapturaLog()], level=0, force=True)
