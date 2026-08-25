from techmunkak.core.db import pool
from techmunkak.ingest.models import JobUrl
from techmunkak.ingest import selectors

def next_for_fetch_stage() -> list[JobUrl]:
    job_urls = []
    with pool().connection() as conn:
        rows = conn.execute("""
            select id, scrape_run_id, site_id, url, url_hash, first_seen_at, last_fetched_at, status, s3_key
            from bronze.job_urls
            where status in ('pending', 'failed')
            and attempts < 5
            and next_attempt_at <= now()
            order by next_attempt_at
            limit 25
            for update skip locked
        """).fetchall()
        
        for row in rows:
            _increase_attempt(conn, id=row[0])
            
            scrape_run = selectors.find_scrape_run(id=row[1])
            site = selectors.find_site(id=row[2])
            
            job_urls.append(JobUrl(
                id=row[0],
                scrape_run=scrape_run,
                site=site,
                url=row[3],
                url_hash=row[4],
                first_seen_at=row[5],
                last_fetched_at=row[6],
                status=row[7],
                s3_key=row[8],
            ))
    
    return job_urls

def next_for_load_stage() -> list[JobUrl]:
    job_urls = []
    with pool().connection() as conn:
        rows = conn.execute("""
            select id, scrape_run_id, site_id, url, url_hash, first_seen_at, last_fetched_at, status, s3_key
            from bronze.job_urls
            where status = 'fetched'
            and attempts < 5
            and next_attempt_at <= now()
            order by next_attempt_at
            limit 100
            for update skip locked
        """).fetchall()
        
        for row in rows:
            _increase_attempt(conn, id=row[0])
            
            scrape_run = selectors.find_scrape_run(id=row[1])
            site = selectors.find_site(id=row[2])
            
            job_urls.append(JobUrl(
                id=row[0],
                scrape_run=scrape_run,
                site=site,
                url=row[3],
                url_hash=row[4],
                first_seen_at=row[5],
                last_fetched_at=row[6],
                status=row[7],
                s3_key=row[8],
            ))
    
    return job_urls

def _increase_attempt(conn, id: int):
    conn.execute("""
        update bronze.job_urls
        set 
            attempts = attempts + 1
        where id = %s
    """, (id,))
    
    conn.commit()