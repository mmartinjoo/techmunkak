from sqlalchemy import desc
from techmunkak.core.db import pool
from techmunkak.enrich.models import JobTranslationResult

def fetch_raw_job_payload(job_key: str) -> dict:
    with pool().connection() as conn:
        row = conn.execute("""
            select raw.id, raw.payload 
            from silver.fact_job as fact            
            join bronze.raw_jobs as raw on raw.id = fact.bronze_id
            where job_key = %s
            limit 1
        """, (job_key,)).fetchone()
        
        return row[1]

def fetch_job_details_for_translation(job_key: str) -> JobTranslationResult:
    with pool().connection() as conn:
        row = conn.execute("""
            select title, description
            from silver.fact_job
            where job_key = %s
            limit 1
        """, (job_key,)).fetchone()
        
        return JobTranslationResult(
            title=row[0],
            description=row[1],
        )