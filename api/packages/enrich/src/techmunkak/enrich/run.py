import logging

from techmunkak.core.logging import setup_logging
from techmunkak.enrich import stages

logger = logging.getLogger(__name__)

def main():
    setup_logging()
    logger.info("enqueueing...")
    count = stages.enqueue_stage()
    logger.info("enqueue done: %s jobs", count)
    
    logger.info("translating...")
    (finished, failed) = stages.translation_stage()
    logger.info("translation done: %s finished, %s failed", finished, failed)
    
    logger.info("extracting main skill...")
    (finished, failed) = stages.main_skill_extraction_stage()
    logger.info("extraction done: %s finished, %s failed", finished, failed)
    
    logger.info("embedding...")
    (finished, failed) = stages.embedding_stage()
    logger.info("embedding done: %s finished, %s failed", finished, failed)
    
def extract():
    logger.info("extracting main skill...")
    (finished, failed) = stages.main_skill_extraction_stage()
    logger.info("extraction done: %s finished, %s failed", finished, failed)
