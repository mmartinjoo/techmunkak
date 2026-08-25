import traceback
from techmunkak.ingest import selectors
from techmunkak.ingest.scrapers import get_scraper
from techmunkak.ingest.services import tracking
from techmunkak.ingest.services.job import create_job
from techmunkak.ingest.services import job_url_queue
from techmunkak.core import storage

def discover_stage(
    site_search_term_id: int, 
    scrape_run_id: int,
) -> tuple[list[int], list[str]]:
    site_search_term = selectors.find_site_search_term(id=site_search_term_id)
    scrape_run = selectors.find_scrape_run(id=scrape_run_id)
    
    scraper = get_scraper(site_name=site_search_term.site.name)
    
    pages = scraper.fetch_search_result_pages(
        site_search_term=site_search_term,
        max_pages=1,
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
        
        urls = scraper.parse_job_urls(
            search_result_page_data=page,
        )
        job_urls.append(urls)
        
    root_urls = scraper.dedupe_job_urls(job_urls=[item for sublist in job_urls for item in sublist])
    job_url_ids = []
    
    for url in root_urls:
        job_url = tracking.create_job_url(
            scrape_run_id=scrape_run.id,
            site_id=site_search_term.site.id,
            url=url,
        )
        
        if job_url is not None:
            job_url_ids.append(job_url.id)
        
    return (job_url_ids, s3_keys)

def fetch_stage(scrape_run_id: int) -> tuple[int, int]:
    scrape_run = selectors.find_scrape_run(id=scrape_run_id)
    scraper = get_scraper(site_name=scrape_run.site.name)
    
    job_urls = job_url_queue.next_for_fetch_stage()

    finished = 0
    failed = 0

    for job_url in job_urls:
        tracking.mark_job_url(
            id=job_url.id,
            status="fetching",
        )
        
        try:
            data = scraper.fetch_job_details(
                url=job_url.url,
            )
            
            key = storage.put_job_details_page(
                site="NoFluffJobs",
                url_hash=job_url.url_hash,
                data=data,
                scrape_run_id=job_url.scrape_run.id,
            )
            
            tracking.update_job_url_s3_key(
                id=job_url.id, 
                s3_key=key,
            )
            
            tracking.mark_job_url(
                id=job_url.id,
                status="fetched",
            )
            
            finished += 1
        except Exception as exc:
            if "404 Client Error" in str(exc):
                tracking.mark_job_url_not_found(
                    id=job_url.id,
                )
            else:
                tracking.mark_job_url_failed(
                    id=job_url.id,
                    error=traceback.format_exc()
                )
            
            failed += 1
    
    return (finished, failed)

def load_stage(scrape_run_id: int):
    scrape_run = selectors.find_scrape_run(id=scrape_run_id)
    scraper = get_scraper(site_name=scrape_run.site.name)
    
    job_urls = job_url_queue.next_for_load_stage()
    
    finished = 0
    failed = 0
    
    for job_url in job_urls:
        tracking.mark_job_url(
            id=job_url.id,
            status="loading",
        )
        
        try:
            content = storage.get_job_details_page(job_url.s3_key)
            
            data = scraper.parse_job_details(
                raw_content=content,
            )
            
            create_job(
                site_name=scrape_run.site.name,
                job_url=job_url,
                data=data,
            )
            
            tracking.mark_job_url(
                id=job_url.id,
                status="finished",
            )
            
            finished += 1
        except Exception:
            tracking.mark_job_url_failed(
                id=job_url.id,
                error=traceback.format_exc(),
            )
            
            failed += 1
            
    return (finished, failed)