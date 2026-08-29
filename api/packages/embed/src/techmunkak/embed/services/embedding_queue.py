from techmunkak.core.db import pool
from techmunkak.embed.models import EmbeddableJob, Job
from techmunkak.embed.services.translation import get_translator

def enqueue_next_batch() -> int:
    """
    Populates the queue with job keys based on new jobs in fact_job
    """
    
    with pool().connection() as conn:
        rows = conn.execute("""
            select jobs.job_key, sites.name
            from silver.fact_job as jobs
            left join ops.embedding_queue as queue on queue.job_key = jobs.job_key
            join bronze.raw_jobs as raw_jobs on raw_jobs.id = jobs.bronze_id
            join ops.sites as sites on sites.id = raw_jobs.site_id
            where queue.job_key is null
        """).fetchall()
        
        for row in rows:
            translator = get_translator(site_name=row[1])
            need_translation = translator.need_translation(job_key=row[0])
            status = "waiting_for_translation" if need_translation else "waiting_for_embedding"
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
                values(%s, 0, now(), %s, false, false, %s)                             
            """, (row[0], need_translation,status,))
            
            conn.commit()
            
    return len(rows)

def dequeue_for_translation(limit=25) -> list[Job]:
    with pool().connection() as conn:
        rows = conn.execute("""
            select fact.job_key, sites.name
            from ops.embedding_queue as queue            
            join silver.fact_job as fact on fact.job_key = queue.job_key
            join bronze.raw_jobs as raw on raw.id = fact.bronze_id
            join ops.sites as sites on sites.id = raw.site_id
            where need_translation is true
            and attempts <= 5
            and next_attempt_at < now()
            and translated = false
            and status in ('waiting_for_translation', 'translation_failed') 
            order by queue.created_at asc
            limit %s
            for update skip locked
        """, (limit,)).fetchall()
        
    return [Job(job_key=row[0], site_name=row[1]) for row in rows]

def mark_translation_in_progress(job_key: str):
    with pool().connection() as conn:
        conn.execute("""
            update ops.embedding_queue
            set
                status = 'translation_in_progress',
                attempts = attempts + 1  
            where job_key = %s
        """, (job_key,))
        
        conn.commit()

def mark_translation_finished(job_key: str):
    with pool().connection() as conn:
        conn.execute("""
            update ops.embedding_queue
            set
                translated = true,
                status = 'waiting_for_embedding',
                translated_at = now()
            where job_key = %s
        """, (job_key,))
        
        conn.commit()
        
def mark_translation_failed(job_key: str, error: str):
    with pool().connection() as conn:
        conn.execute("""
            update ops.embedding_queue
            set
                translated = false,
                status = 'translation_failed',
                next_attempt_at = now() + interval '5 hours',
                error = %s
            where job_key = %s
        """, (error, job_key,))
        
        conn.commit()
        
def dequeue_for_embedding(limit=25) -> list[Job]:
    with pool().connection() as conn:
        rows = conn.execute("""
            select 
                fact.job_key,
                case 
                	when translated.id is null then concat_ws(' ', fact.title, fact.description)
                	else concat_ws(' ', translated.title_translated, translated.description_translated)
                end as content           
            from ops.embedding_queue as queue    
                    
            join silver.fact_job as fact on fact.job_key = queue.job_key
            left join ops.translated_jobs as translated on translated.job_key = fact.job_key
            
            where attempts <= 5
            and next_attempt_at < now()
            and status in ('waiting_for_embedding', 'embedding_failed')
            order by queue.created_at asc
            limit %s
            for update of queue skip locked
        """, (limit,)).fetchall()
        
    return [
        EmbeddableJob(
            job_key=row[0], 
            content=row[1],
        ) 
        for row in rows
    ]
    
def mark_embedding_in_progress(job_key: str):
    with pool().connection() as conn:
        conn.execute("""
            update ops.embedding_queue
            set
                status = 'embedding_in_progress',
                attempts = attempts + 1
            where job_key = %s
        """, (job_key,))
        
        conn.commit()

def mark_embedding_finished(job_key: str):
    with pool().connection() as conn:
        conn.execute("""
            update ops.embedding_queue
            set
                embedded = true,
                status = 'finished',
                embedded_at = now()
            where job_key = %s
        """, (job_key,))
        
        conn.commit()
        
def mark_embedding_failed(job_key: str, error: str):
    with pool().connection() as conn:
        conn.execute("""
            update ops.embedding_queue
            set
                embedded = false,
                status = 'embedding_failed',
                next_attempt_at = now() + interval '5 hours',
                error = %s
            where job_key = %s
        """, (error, job_key,))
        
        conn.commit()