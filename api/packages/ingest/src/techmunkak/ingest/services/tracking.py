import hashlib
import json

from techmunkak.core.db import pool
from techmunkak.ingest import selectors
from techmunkak.ingest.models import JobUrl

def create_scrape_run(site_id: int, search_term_id: int):
    with pool().connection() as conn:
        row = conn.execute("""
            insert into ops.scrape_runs(site_id, search_term_id)
            values (%s, %s)          
            returning id
        """, (site_id, search_term_id,)).fetchone()
        
        conn.commit()
        
        return selectors.find_scrape_run(id=row[0])
    
def update_discovered_count(scrape_run_id: int, discovered_count: int):
    with pool().connection() as conn:
        conn.execute("""
            update ops.scrape_runs
            set 
                discovered_count = %s,
                status = %s
            where id = %s             
        """, (discovered_count, "discovered", scrape_run_id,))
        
        conn.commit()
        
def update_s3_keys(scrape_run_id: int, s3_keys: list[str]):
    with pool().connection() as conn:
        conn.execute(
            """
                update ops.scrape_runs
                set 
                    s3_keys = %s
                where id = %s             
            """, 
            (
                json.dumps(s3_keys), 
                scrape_run_id,
            ),
        )
        
        conn.commit()
        
def create_job_url(scrape_run_id: int, site_id: int, url: str) -> JobUrl | None:
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
    with pool().connection() as conn:
        row = conn.execute("""
            insert into bronze.job_urls(scrape_run_id, site_id, url, url_hash, first_seen_at, last_fetched_at)
            values(%s, %s, %s, %s, now(), now())
            returning id
        """, (
            scrape_run_id,
            site_id,
            url,
            url_hash,            
        )).fetchone()
        
        conn.commit()
        
        return selectors.find_job_url(id=row[0])
        
def mark_job_url(id: int, status: str):
    with pool().connection() as conn:
        conn.execute("""
            update bronze.job_urls
            set 
                status = %s
            where id = %s
        """, (status, id,))
        
        conn.commit()
        
def mark_job_url_failed(id: int, error: str):
    with pool().connection() as conn:
        conn.execute("""
            update bronze.job_urls
            set 
                status = 'failed',
                error = %s,
                next_attempt_at = next_attempt_at + interval '5 hours'
            where id = %s
        """, (error, id,))
        
        conn.commit()
        
def mark_job_url_not_found(id: int):
    with pool().connection() as conn:
        conn.execute("""
            update bronze.job_urls
            set 
                status = 'not_found'
            where id = %s
        """, (id,))
        
        conn.commit()
        
def update_job_url_s3_key(id: int, s3_key: str):
    with pool().connection() as conn:
        conn.execute("""
            update bronze.job_urls
            set 
                s3_key = %s
            where id = %s
        """, (s3_key, id,))
        
        conn.commit()
        
def mark_scrape_run(scrape_run_id: int, status: str):
    with pool().connection() as conn:
        conn.execute("""
            update ops.scrape_runs
            set 
                status = %s
            where id = %s             
        """, (status, scrape_run_id,))
        
        conn.commit()
        
    if status == "finished":
        with pool().connection() as conn:
            conn.execute("""
                update ops.scrape_runs
                set 
                    finished_at = now()
                where id = %s             
            """, (scrape_run_id,))
            
            conn.commit()
        
def update_site_search_term_last_run_at(site_search_term_id: int):
    with pool().connection() as conn:
        conn.execute("""
            update ops.site_search_terms
            set 
                last_run_at = now()
            where id = %s             
        """, (site_search_term_id,))
        
        conn.commit()