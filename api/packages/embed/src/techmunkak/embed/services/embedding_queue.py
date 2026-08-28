from techmunkak.core.db import pool


def enqueue_next_batch():
    """
    Populates the queue with job keys based on new jobs in fact_job
    """
    
    with pool().connection() as conn:
        rows = conn.execute("""
            select jobs.job_key
            from silver.fact_job jobs
            left join ops.embedding_queue queue on queue.job_key = jobs.job_key
            where queue.job_key is null             
        """)
        
        for row in rows:
            conn.execute("""
                insert into ops.embedding_queue(
                    job_key,
                    attempts,
                    next_attempt_at,
                    need_translation,
                    translated,
                    embedded,
                    status
                )
                values(%s, 0, now(), false, true, false, 'pending')                             
            """, (row[0],))
            
            conn.commit()