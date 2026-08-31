import pendulum
from datetime import timedelta
from airflow.sdk import dag, task
from techmunkak.ingest import run
from techmunkak.core.config import settings

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