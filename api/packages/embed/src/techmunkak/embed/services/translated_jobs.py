from techmunkak.core.db import pool
from techmunkak.embed.models import JobTranslationResult


def create_translated_job(job_key: str, job_translation_result: JobTranslationResult):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.translated_jobs(job_key, title_translated, description_translated, created_at)
            values(%s, %s, %s, now())             
        """, (
            job_key,
            job_translation_result.title,
            job_translation_result.description,
        ))
        
        conn.commit()