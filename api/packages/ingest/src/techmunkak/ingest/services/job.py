from techmunkak.core.db import pool
from techmunkak.ingest.models import JobUrl

def create_raw_job(
    site_id: int, 
    job_url: JobUrl,
    payload_json: str,
):
    with pool().connection() as conn:
        conn.execute("""
            insert into bronze.raw_jobs(site_id, job_url_id, url, payload, fetched_at)
            values(%s, %s, %s, %s, %s)             
        """, (site_id, job_url.id, job_url.url, payload_json, job_url.last_fetched_at,))
        
        conn.commit()
