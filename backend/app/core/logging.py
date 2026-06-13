import logging
from logging.config import dictConfig

from .config import settings


def setup_logging() -> None:
    level = "DEBUG" if settings.DEBUG else "INFO"
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
        },
        "handlers": {
            "default": {
                "level": level,
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "": {"handlers": ["default"], "level": level, "propagate": False},
        },
    }
    dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

