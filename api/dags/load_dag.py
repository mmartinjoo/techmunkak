import pendulum
from datetime import timedelta
from airflow.sdk import dag, task
from techmunkak.ingest import run

@dag(
    dag_id="load",
    start_date=pendulum.datetime(2026, 8, 29, tz="UTC"),
    schedule=timedelta(minutes=15),
    catchup=False,
)
def load():
    @task
    def load():
        run.load()
        
    load()
    
load()