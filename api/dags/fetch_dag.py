import pendulum
from datetime import timedelta
from airflow.sdk import dag, task
from techmunkak.ingest import run

@dag(
    dag_id="fetch",
    start_date=pendulum.datetime(2026, 8, 29, tz="UTC"),
    schedule=timedelta(minutes=30),
    catchup=False,
)
def fetch():
    @task
    def fetch():
        run.fetch()
        
    fetch()
    
fetch()