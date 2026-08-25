from techmunkak.core.db import pool

def create_raw_job(
    site_id: int, 
    scrape_run_id: int,
    job_url_id: int,
    payload_json: str,
):
    with pool().connection() as conn:
        conn.execute("""
            insert into bronze.raw_jobs(site_id, scrape_run_id, job_url_id, payload)
            values(%s, %s, %s, %s)             
        """, (site_id, scrape_run_id, job_url_id, payload_json))
        
        conn.commit()
