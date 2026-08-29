from techmunkak.core.db import pool
from techmunkak.ingest.models import JobUrl
from techmunkak.ingest import selectors


def enqueue(job_url: JobUrl):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.ingestion_queue(job_url_id, attempts, next_attempt_at, fetched, loaded, status, discovered_at, created_at)
            values(%s, 0, now(), false, false, %s, now(), now())             
        """, (
            job_url.id,
            'waiting_for_fetch',
        ))
        
        conn.commit()
        
def dequeue_for_fetching(limit=25) -> list[JobUrl]:
    job_urls = []
    with pool().connection() as conn:
        rows = conn.execute("""
            select job_url_id
            from ops.ingestion_queue
            where fetched = false
            and status in ('waiting_for_fetch', 'fetch_failed')   
            and attempts <= 5
            and next_attempt_at <= now()
            order by created_at asc
            limit %s
            for update skip locked
        """, (limit,)).fetchall()
        
        for row in rows:
            job_urls.append(selectors.find_job_url(id=row[0]))
        
    return job_urls

def dequeue_for_loading(limit=25) -> list[JobUrl]:
    job_urls = []
    with pool().connection() as conn:
        rows = conn.execute("""
            select job_url_id
            from ops.ingestion_queue
            where fetched = true
            and loaded = false
            and status in ('waiting_for_load', 'load_failed')   
            and attempts <= 5
            and next_attempt_at <= now()
            order by created_at asc
            limit %s
            for update skip locked
        """, (limit,)).fetchall()
        
        for row in rows:
            job_urls.append(selectors.find_job_url(id=row[0]))        
        
    return job_urls

def mark_fetch_in_progress(job_url: JobUrl):
    with pool().connection() as conn:
        conn.execute("""
            update ops.ingestion_queue
            set
                status = 'fetch_in_progress',
                attempts = attempts + 1
            where job_url_id = %s
        """, (job_url.id,))

def mark_fetch_finished(job_url: JobUrl):
    with pool().connection() as conn:
        conn.execute("""
            update ops.ingestion_queue
            set
                fetched = true,
                status = 'waiting_for_load',
                fetched_at = now()
            where job_url_id = %s
        """, (job_url.id,))
        
def mark_fetch_failed(job_url: JobUrl, error: str):
    with pool().connection() as conn:
        conn.execute("""
            update ops.ingestion_queue
            set
                fetched = false,
                status = 'fetch_failed',
                next_attempt_at = now() + interval '5 hours',
                error = %s
            where job_url_id = %s
        """, (error, job_url.id,))
        
def mark_fetch_not_fonud(job_url: JobUrl):
    with pool().connection() as conn:
        conn.execute("""
            update ops.ingestion_queue
            set
                fetched = false,
                status = 'fetch_failed',
                next_attempt_at = null,
                error = 'not_found'
            where job_url_id = %s
        """, (job_url.id,))
        
def mark_load_in_progress(job_url: JobUrl):
    with pool().connection() as conn:
        conn.execute("""
            update ops.ingestion_queue
            set
                status = 'load_in_progress',
                attempts = attempts + 1
            where job_url_id = %s
        """, (job_url.id,))

def mark_load_finished(job_url: JobUrl):
    with pool().connection() as conn:
        conn.execute("""
            update ops.ingestion_queue
            set
                loaded = true,
                status = 'finished',
                loaded_at = now()
            where job_url_id = %s
        """, (job_url.id,))
        
def mark_load_failed(job_url: JobUrl, error: str):
    with pool().connection() as conn:
        conn.execute("""
            update ops.ingestion_queue
            set
                loaded = false,
                status = 'load_failed',
                next_attempt_at = now() + interval '5 hours',
                error = %s
            where job_url_id = %s
        """, (error, job_url.id,))