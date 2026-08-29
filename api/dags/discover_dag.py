import pendulum
from airflow.sdk import task, dag, task_group
from techmunkak.ingest.models import SiteSearchTerm
from techmunkak.ingest import run

@dag(
    dag_id="discover_dag",
    start_date=pendulum.datetime(2026, 8, 29, tz="UTC"),
    catchup=False,
    schedule="@daily",
)
def discover():
    @task_group
    def ingest_site_search_term(site_search_term: SiteSearchTerm):
        @task
        def discover_one(site_search_term: SiteSearchTerm) -> list[int]:
            return run.discover_one(site_search_term=site_search_term)
            
        return discover_one(site_search_term=site_search_term)
    
    ingest_site_search_term.expand(site_search_term=run.fetch_next_site_search_terms())

discover()