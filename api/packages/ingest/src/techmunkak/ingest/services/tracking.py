import hashlib

from techmunkak.core.db import pool
from techmunkak.ingest import selectors
from techmunkak.ingest.models import JobUrl

def create_job_url(site_id: int, url: str) -> JobUrl | None:
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
    with pool().connection() as conn:
        row = conn.execute("""
            insert into bronze.job_urls(site_id, url, url_hash, first_seen_at, last_fetched_at)
            values(%s, %s, %s, now(), now())
            returning id
        """, (
            site_id,
            url,
            url_hash,            
        )).fetchone()
        
        conn.commit()
        
        return selectors.find_job_url(id=row[0])
        
def update_job_url_s3_key(id: int, s3_key: str):
    with pool().connection() as conn:
        conn.execute("""
            update bronze.job_urls
            set 
                s3_key = %s
            where id = %s
        """, (s3_key, id,))
        
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