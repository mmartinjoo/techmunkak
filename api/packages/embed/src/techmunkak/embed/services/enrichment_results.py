import json
from techmunkak.core.db import pool
from techmunkak.embed.models import JobTranslationResult

def upsert_chroma_ids(job_key: str, chroma_ids: list[str]):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.enrichment_results(job_key, chroma_embedding_ids)
            values(%s, %s)             
            on conflict (job_key) 
            do update
                set chroma_embedding_ids = %s
        """, (job_key, json.dumps(chroma_ids), json.dumps(chroma_ids),))
        
        _mark_finished(job_key=job_key, conn=conn)
        
        conn.commit()
        
def upsert_transations(job_key: str, job_translation_result: JobTranslationResult):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.enrichment_results(job_key, title_en, description_en)
            values(%s, %s, %s)
            on conflict (job_key)
            do update
            set
                title_en = %s,
                description_en = %s
        """, (
            job_key,
            job_translation_result.title,            
            job_translation_result.description,
            job_translation_result.title,
            job_translation_result.description,
        ))
        
        _mark_finished(job_key=job_key, conn=conn)
        
        conn.commit()
        
def upsert_main_skill(job_key: str, main_skill_site_suggested: str, main_skill_nlp_suggested: str):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.enrichment_results(job_key, main_skill_site_suggested, main_skill_nlp_suggested)
            values(%s, %s, %s)             
            on conflict (job_key) 
            do update
                set main_skill_site_suggested = %s,
                main_skill_nlp_suggested = %s
        """, (
            job_key, 
            main_skill_site_suggested, 
            main_skill_nlp_suggested,
            main_skill_site_suggested, 
            main_skill_nlp_suggested,
        ))
        
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