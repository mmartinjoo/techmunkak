import logging

from techmunkak.core.logging import setup_logging

logger = logging.getLogger(__name__)

def embed():
    setup_logging()
    logger.info("embed")
