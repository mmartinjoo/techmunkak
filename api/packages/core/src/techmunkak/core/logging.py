import logging
import sys

from techmunkak.core.config import settings


def setup_logging() -> None:
    """Configure root logging once, at an application entry point.

    Idempotent: if the root logger already has handlers (e.g. under Airflow,
    which configures its own logging), this is a no-op.
    """
    logging.basicConfig(
        handlers=[
            logging.FileHandler(filename="/var/log/techmunkak.log", encoding="utf-8"),
            logging.StreamHandler(stream=sys.stdout),
        ],
        level=getattr(logging, settings.log_level.upper()),
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    )
