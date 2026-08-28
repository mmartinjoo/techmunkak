from techmunkak.ingest import selectors
from techmunkak.ingest.services import tracking
from techmunkak.ingest import stages

def run() -> tuple[int, int]:
    next_site_search_terms = selectors.fetch_next_site_search_terms()
    for site_search_term in next_site_search_terms:
        scrape_run = tracking.create_scrape_run(
            site_id=site_search_term.site.id,
            search_term_id=site_search_term.search_term.id,
        )
        
        (job_url_ids, s3_keys) = stages.discover_stage(
            site_search_term_id=site_search_term.id,
            scrape_run_id=scrape_run.id,
        )
        
        tracking.update_discovered_count(
            scrape_run_id=scrape_run.id,
            discovered_count=len(job_url_ids),
        )
        tracking.update_s3_keys(
            scrape_run_id=scrape_run.id,
            s3_keys=s3_keys,
        )
        
        stages.fetch_stage(scrape_run_id=scrape_run.id)
        
        tracking.mark_scrape_run(
            scrape_run_id=scrape_run.id,
            status="fetched",
        )
        
        (finished, failed) = stages.load_stage(scrape_run_id=scrape_run.id)
        
        tracking.mark_scrape_run(
            scrape_run_id=scrape_run.id,
            status="finished",
        )
        
        tracking.update_site_search_term_last_run_at(
            site_search_term_id=site_search_term.id,
        )
        
    return (finished, failed)