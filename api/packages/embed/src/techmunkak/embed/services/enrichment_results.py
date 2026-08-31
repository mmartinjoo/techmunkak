import json
from techmunkak.core.db import pool
from techmunkak.embed.models import JobTranslationResult

def update_translation(job_key: str, job_translation_result: JobTranslationResult):
    with pool().connection() as conn:
        conn.execute("""
            update ops.enrichment_results
            set 
                title_en = %s, 
                description_en = %s
            where job_key = %s
        """, (
            job_translation_result.title,            
            job_translation_result.description,
            job_key,
        ))
        
        _mark_finished(job_key=job_key, conn=conn)
        
        conn.commit()
        
def update_main_skill(job_key: str, main_skill_site_suggested: str, main_skill_nlp_suggested: str):
    with pool().connection() as conn:
        conn.execute("""
            update ops.enrichment_results
            set 
                main_skill_site_suggested = %s,
                main_skill_nlp_suggested = %s
            where job_key = %s
        """, (
            main_skill_site_suggested, 
            main_skill_nlp_suggested,
            job_key, 
        ))
        
        _mark_finished(job_key=job_key, conn=conn)
        
        conn.commit()

def update_chroma_ids(job_key: str, chroma_ids: list[str]):
    with pool().connection() as conn:
        conn.execute("""
            update ops.enrichment_results
            set 
                chroma_embedding_ids = %s
            where job_key = %s
        """, (json.dumps(chroma_ids), job_key,))
        
        _mark_finished(job_key=job_key, conn=conn)
        
        conn.commit()
        
def _mark_finished(job_key: str, conn):
    conn.execute("""
        update ops.enrichment_results
        set ready = true
        where job_key = %s
        and title_en is not null
        and description_en is not null
        and chroma_embedding_ids is not null
        and (
            main_skill_site_suggested is not null
            or
            main_skill_nlp_suggested is not null	
        )
    """, (job_key,))