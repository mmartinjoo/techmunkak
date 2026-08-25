import traceback
from techmunkak.ingest import selectors, services
from techmunkak.ingest.scrapers import nofluffjobs

def discover_stage(
    site_search_term_id: int, 
    scrape_run_id: int,
) -> list[int]:
    site_search_term = selectors.find_site_search_term(id=site_search_term_id)
    scrape_run = selectors.find_scrape_run(id=scrape_run_id)
    
    job_url_ids = []
    
    if site_search_term.site.name != "NoFluffJobs":
        return []
    
    urls = nofluffjobs.discover(
        site_search_term=site_search_term,
        scrape_run_id=scrape_run.id,
    )
    
    for url in urls:
        job_url = services.create_job_url(
            scrape_run_id=scrape_run.id,
            site_id=site_search_term.site.id,
            url=url,
        )
        
        if job_url is not None:
            job_url_ids.append(job_url.id)
        
    return job_url_ids

def fetch_stage(scrape_run_id: int) -> tuple[int, int]:
    job_urls = selectors.fetch_pending_job_urls_by_scrape_run(scrape_run_id=scrape_run_id)

    finished = 0
    failed = 0

    for job_url in job_urls:
        services.mark_job_url(
            id=job_url.id,
            status="fetching",
        )
        
        try:
            nofluffjobs.fetch_job_details(
                job_url_id=job_url.id,
            )
            services.mark_job_url(
                id=job_url.id,
                status="fetched",
            )
            
            finished += 1
        except Exception as exc:
            status = "failed"
            if "404 Client Error" in str(exc):
                status = "not_found"
                
            services.mark_job_url(
                id=job_url.id,
                status=status,
                error=traceback.format_exc()
            )
            
            failed += 1
    
    return (finished, failed)