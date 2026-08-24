from techmunkak.ingest import selectors
from techmunkak.ingest import services
from techmunkak.ingest.scrapers import nofluffjobs

def run():
    next_site_search_terms = selectors.fetch_next_site_search_terms()
    for site_search_term in next_site_search_terms:
        if site_search_term.site.name != "NoFluffJobs":
            continue
        
        scrape_run = services.create_scrape_run(
            site_id=site_search_term.site.id,
            search_term_id=site_search_term.search_term.id,
        )
        
        job_urls = nofluffjobs.discover(
            site_search_term=site_search_term,
            scrape_run_id=scrape_run.id,
        )
        
        services.update_discovered_count(
            scrape_run_id=scrape_run.id,
            discovered_count=len(job_urls),
        )
        
        for job_url in job_urls:
            services.add_scrape_run_item(
                scrape_run_id=scrape_run.id,
                site_id=site_search_term.site.id,
                url=job_url,
            )