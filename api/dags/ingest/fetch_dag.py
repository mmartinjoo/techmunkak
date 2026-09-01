from datetime import timedelta

import pendulum
from airflow.sdk import dag, task
from techmunkak.core.config import settings
from techmunkak.core.logging import setup_logging
from techmunkak.ingest import run

setup_logging()

@dag(
    dag_id="fetch",
    start_date=pendulum.datetime(2026, 8, 29, tz="UTC"),
    schedule=timedelta(minutes=settings.scheduler_fetch_schedule_minutes),
    catchup=False,
)
def fetch():
    @task
    def fetch():
        run.fetch()
        
    fetch()
    
fetch()