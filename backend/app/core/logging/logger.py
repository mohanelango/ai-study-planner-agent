import logging
import sys

from app.core.config.settings import settings


LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO if settings.APP_ENV != "development" else logging.DEBUG,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

