import logging

from techmunkak.core.logging import setup_logging
from techmunkak.ingest import selectors, stages
from techmunkak.ingest.services import tracking
from techmunkak.ingest.services.currency_conversion import refresh_exchange_rates

logger = logging.getLogger(__name__)

def discover():
    setup_logging()
    for id in selectors.fetch_next_site_search_term_ids():
        discover_one(site_search_term_id=id)    
    
def fetch() -> tuple[int, int]:
    setup_logging()
    logger.info("fetching...")
    (finished, failed) = stages.fetch_stage()
    logger.info("fetch done: %s finished, %s failed", finished, failed)
    
def load() -> tuple[int, int]:
    setup_logging()
    logger.info("loading...")
    (finished, failed) = stages.load_stage()
    logger.info("load done: %s finished, %s failed", finished, failed)
    
def run_refresh_exchange_rates():
    setup_logging()
    logger.info("refreshing exchange rates")
    count = refresh_exchange_rates()
    logger.info("refreshing done: %s refreshed", count)
    
def discover_one(site_search_term_id: int) -> list[int]:
    site_search_term = selectors.find_site_search_term(id=site_search_term_id)
    
    logger.info('discovering %s with search term "%s"', site_search_term.site.name, site_search_term.search_term.term)
    
    job_url_ids = stages.discover_stage(
        site_search_term_id=site_search_term.id,
    )        
    
    tracking.update_site_search_term_last_run_at(
        site_search_term_id=site_search_term.id,
    )
    logger.info("discovered %s URLs", len(job_url_ids))
    
    return job_url_ids
