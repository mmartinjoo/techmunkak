import pendulum
from datetime import timedelta
from airflow.sdk import task, dag, task_group
from techmunkak.ingest import run
from techmunkak.ingest import selectors

@dag(
    dag_id="discover",
    start_date=pendulum.datetime(2026, 8, 29, tz="UTC"),
    catchup=False,
    schedule=timedelta(hours=1),
)
def discover():
    @task_group
    def discover_task_group(site_search_term_id: int):
        @task
        def discover_one(site_search_term_id: int) -> list[int]:
            return run.discover_one(site_search_term_id=site_search_term_id)
            
        return discover_one(site_search_term_id=site_search_term_id)
    
    @task
    def select() -> list[int]:
        return selectors.fetch_next_site_search_term_ids()
    
    select() >> discover_task_group.expand(site_search_term_id=select())

discover()