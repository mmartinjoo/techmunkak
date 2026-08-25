import traceback
from techmunkak.ingest import selectors
from techmunkak.ingest.scrapers import nofluffjobs
from techmunkak.ingest.services import tracking
import techmunkak.ingest.services.nofluffjobs as nofluffjobs_services
from techmunkak.core import storage

def discover_stage(
    site_search_term_id: int, 
    scrape_run_id: int,
) -> tuple[list[int], list[str]]:
    site_search_term = selectors.find_site_search_term(id=site_search_term_id)
    scrape_run = selectors.find_scrape_run(id=scrape_run_id)
    
    pages = nofluffjobs.fetch_search_result_pages(
        site_search_term=site_search_term,
    )
    
    job_urls = []
    s3_keys = []
    for i, page in enumerate(pages):
        key = storage.put_listing_page(
            site="NoFluffJobs",
            search_term=site_search_term.search_term.term,
            data=page,
            page=i+1,
            scrape_run_id=scrape_run_id,
        )
        s3_keys.append(key)
        
        urls = nofluffjobs.parse_job_urls(
            search_result_page_data=page,
        )
        job_urls.append(urls)
        
    flat_job_urls = [item for sublist in job_urls for item in sublist]
    job_url_ids = []
    
    for url in flat_job_urls:
        job_url = tracking.create_job_url(
            scrape_run_id=scrape_run.id,
            site_id=site_search_term.site.id,
            url=url,
        )
        
        if job_url is not None:
            job_url_ids.append(job_url.id)
        
    return (job_url_ids, s3_keys)

def fetch_stage(scrape_run_id: int) -> tuple[int, int]:
    job_urls = selectors.fetch_job_urls(scrape_run_id=scrape_run_id, status='pending')

    finished = 0
    failed = 0

    for job_url in job_urls:
        tracking.mark_job_url(
            id=job_url.id,
            status="fetching",
        )
        
        try:
            nofluffjobs.fetch_job_details(
                job_url_id=job_url.id,
            )
            tracking.mark_job_url(
                id=job_url.id,
                status="fetched",
            )
            
            finished += 1
        except Exception as exc:
            status = "failed"
            if "404 Client Error" in str(exc):
                status = "not_found"
                
            tracking.mark_job_url(
                id=job_url.id,
                status=status,
                error=traceback.format_exc()
            )
            
            failed += 1
    
    return (finished, failed)

def load_stage(scrape_run_id: int):
    job_urls = selectors.fetch_job_urls(scrape_run_id=scrape_run_id, status='fetched')
    
    finished = 0
    failed = 0
    
    for job_url in job_urls:
        tracking.mark_job_url(
            id=job_url.id,
            status="loading",
        )
        
        try:
            data = nofluffjobs.parse_job_details(
                job_url_id=job_url.id,
            )
            
            nofluffjobs_services.create_job(job_url_id=job_url.id, data=data)
            
            tracking.mark_job_url(
                id=job_url.id,
                status="finished",
            )
            
            finished += 1
        except Exception:
            tracking.mark_job_url(
                id=job_url.id,
                status="failed",
                error=traceback.format_exc()
            )
            
            failed += 1
            
    return (finished, failed)