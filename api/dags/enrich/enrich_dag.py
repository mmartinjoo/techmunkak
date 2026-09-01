import logging
from datetime import timedelta

import pendulum
from airflow.sdk import Asset, dag, task
from techmunkak.core.logging import setup_logging
from techmunkak.enrich.stages import (
    embedding_stage,
    enqueue_stage,
    main_skill_extraction_stage,
    translation_stage,
)

logger = logging.getLogger(__name__)

setup_logging()

@dag(
    dag_id="enrich",
    start_date=pendulum.datetime(2026, 8, 28, tz="UTC"),
    catchup=False,
    schedule=Asset("x-fact-job://ready")
)
def embed():
    @task(retries=3, retry_delay=timedelta(minutes=3))
    def enqueue() -> int:
        count = enqueue_stage()
        logger.info("enqueued %s jobs", count)
        return count
        
    @task(retries=3, retry_delay=timedelta(minutes=15))
    def translate() -> tuple[int, int]:
        (finished, failed) = translation_stage()
        logger.info("translate: %s finished, %s failed", finished, failed)
        return (finished, failed)
    
    @task(retries=3, retry_delay=timedelta(minutes=15))
    def main_skill_extraction() -> tuple[int, int]:
        (finished, failed) = main_skill_extraction_stage()
        logger.info("main skill extraction: %s finished, %s failed", finished, failed)
        return (finished, failed)
    
    @task(retries=3, retry_delay=timedelta(minutes=10), outlets=[Asset("x-enrichment-results://ready")])
    def embed():
        (finished, failed) = embedding_stage()
        logger.info("embed: %s finished, %s failed", finished, failed)
        return (finished, failed)
    
    enqueue() >> translate() >> main_skill_extraction() >> embed()
        
embed()
