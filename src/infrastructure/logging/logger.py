import logging
import sys

from config import settings


def setup_logging() -> None:
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.getLogger("uvicorn.access").setLevel(level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
