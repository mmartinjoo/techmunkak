import json
from techmunkak.core.db import pool
from techmunkak.embed.models import JobTranslationResult

def upsert_chroma_ids(job_key: str, chroma_ids: list[str]):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.enriched_jobs(job_key, chroma_embedding_ids)
            values(%s, %s)             
            on conflict (job_key) 
            do update
            set chroma_embedding_ids = %s
        """, (job_key, json.dumps(chroma_ids), json.dumps(chroma_ids),))
        
        conn.commit()
        
def upsert_transations(job_key: str, job_translation_result: JobTranslationResult):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.enriched_jobs(job_key, title_translated, description_translated)
            values(%s, %s, %s)
            on conflict (job_key)
            do update
            set
                title_translated = %s,
                description_translated = %s
        """, (
            job_key,
            job_translation_result.title,            
            job_translation_result.description,
            job_translation_result.title,
            job_translation_result.description,
        ))
        
        conn.commit()
        
def upsert_main_skill(job_key: str, main_skill_site_suggested: str, main_skill_nlp_suggested: str):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.enriched_jobs(job_key, main_skill_site_suggested, main_skill_nlp_suggested)
            values(%s, %s, %s)             
            on conflict (job_key) 
            do update
            set main_skill_site_suggested = %s,
            set main_skill_nlp_suggested = %s
        """, (
            job_key, 
            main_skill_site_suggested, 
            main_skill_nlp_suggested,
            main_skill_site_suggested, 
            main_skill_nlp_suggested,
        ))
        
        conn.commit()