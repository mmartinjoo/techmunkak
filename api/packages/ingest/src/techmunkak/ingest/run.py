from techmunkak.ingest.services.currency_conversion import refresh_exchange_rates
from techmunkak.ingest import selectors
from techmunkak.ingest.services import tracking
from techmunkak.ingest import stages

def discover():
    next_site_search_terms = selectors.fetch_next_site_search_terms()
    for site_search_term in next_site_search_terms:
        print(f"discovering {site_search_term.site.name} with search term \"{site_search_term.search_term.term}\"")
        job_url_ids = stages.discover_stage(
            site_search_term_id=site_search_term.id,
        )        
        
        tracking.update_site_search_term_last_run_at(
            site_search_term_id=site_search_term.id,
        )
        print(f"discovered {len(job_url_ids)} URLs")
    
def fetch() -> tuple[int, int]:
    print("fetching...")
    (finished, failed) = stages.fetch_stage()
    print(f"fetch done: {finished} finished, {failed} failed")
    
def load() -> tuple[int, int]:
    print("loading...")
    (finished, failed) = stages.load_stage()
    print(f"load done: {finished} finished, {failed} failed")
    
def run_refresh_exchange_rates():
    print("refreshing exchange rates")
    count = refresh_exchange_rates()
    print(f"refreshing done: {count} refreshed")