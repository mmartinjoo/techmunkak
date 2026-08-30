from datetime import datetime
import traceback
from techmunkak.ingest import selectors
from techmunkak.ingest.scrapers import get_scraper
from techmunkak.ingest.services import tracking, ingestion_queue
from techmunkak.ingest.services.job import create_raw_job
from techmunkak.core import storage

def discover_stage(
    site_search_term_id: int, 
) -> list[str]:
    site_search_term = selectors.find_site_search_term(id=site_search_term_id)
    scraper = get_scraper(site_name=site_search_term.site.name)
    
    pages = scraper.fetch_search_result_pages(
        site_search_term=site_search_term,
        max_pages=10,
        per_page_limit=30,
    )
    
    job_urls = []
    s3_keys = []
    for i, page in enumerate(pages):
        key = storage.put_listing_page(
            site=scraper.get_site_name(),
            search_term=site_search_term.search_term.term,
            data=page,
            page=i+1,
            timestamp=int(datetime.now().timestamp()),
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
            site_id=site_search_term.site.id,
            url=url,
        )
        ingestion_queue.enqueue(job_url=job_url)
        
        job_url_ids.append(job_url.id)
        
    return job_url_ids

def fetch_stage() -> tuple[int, int]:    
    job_urls = ingestion_queue.dequeue_for_fetching()

    finished = 0
    failed = 0

    for job_url in job_urls:
        try:
            scraper = get_scraper(site_name=job_url.site.name)
            ingestion_queue.mark_fetch_in_progress(job_url=job_url)            
            data = scraper.fetch_job_details(
                url=job_url.url,
            )
            
            key = storage.put_job_details_page(
                site=job_url.site.name,
                url_hash=job_url.url_hash,
                data=data,
                timestamp=int(datetime.now().timestamp()),
            )
            
            tracking.update_job_url_s3_key(
                id=job_url.id, 
                s3_key=key,
            )
            
            ingestion_queue.mark_fetch_finished(job_url=job_url)
            
            finished += 1
        except Exception as exc:
            if "404 Client Error" in str(exc):
                ingestion_queue.mark_fetch_not_fonud(job_url=job_url)
            else:
                ingestion_queue.mark_fetch_failed(job_url=job_url, error=traceback.format_exc())
            
            failed += 1
    
    return (finished, failed)

def load_stage() -> tuple[int, int]:
    job_urls = ingestion_queue.dequeue_for_loading()
    
    finished = 0
    failed = 0
    
    for job_url in job_urls:
        try:
            ingestion_queue.mark_load_in_progress(job_url=job_url)
            content = storage.get_job_details_page(job_url.s3_key)
            
            create_raw_job(
                site_id=job_url.site.id,
                job_url=job_url,
                payload_json=content,
            )
            
            ingestion_queue.mark_load_finished(job_url=job_url)
            finished += 1
        except Exception:
            ingestion_queue.mark_load_failed(job_url=job_url, error=traceback.format_exc())
            failed += 1
            
    return (finished, failed)