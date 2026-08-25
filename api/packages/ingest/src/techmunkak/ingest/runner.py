from techmunkak.ingest import selectors
from techmunkak.ingest import services
from techmunkak.ingest import stages

def run():
    next_site_search_terms = selectors.fetch_next_site_search_terms()
    for site_search_term in next_site_search_terms:
        scrape_run = services.create_scrape_run(
            site_id=site_search_term.site.id,
            search_term_id=site_search_term.search_term.id,
        )
        
        job_url_ids = stages.discover_stage(
            site_search_term_id=site_search_term.id,
            scrape_run_id=scrape_run.id,
        )
        
        services.update_discovered_count(
            scrape_run_id=scrape_run.id,
            discovered_count=len(job_url_ids),
        )
        
        stages.fetch_stage(scrape_run_id=scrape_run.id)
        
        services.mark_scrape_run(
            scrape_run_id=scrape_run.id,
            status="fetched",
        )