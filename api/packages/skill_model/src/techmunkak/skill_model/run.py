import logging

from techmunkak.core.logging import setup_logging
from techmunkak.skill_model.services.train import train_skill_model

logger = logging.getLogger(__name__)

def train():
    setup_logging()
    logger.info("training skill model...")
    train_skill_model()
    logger.info("training finished")
