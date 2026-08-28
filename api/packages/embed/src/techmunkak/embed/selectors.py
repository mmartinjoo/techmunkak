from techmunkak.core.db import pool


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