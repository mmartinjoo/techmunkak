from techmunkak.core.db import pool
from techmunkak.embed.models import MainSkillExtractionResult
from techmunkak.nlp.services import inference

SITE_NAME = "JustJoinIT"

def extract(job_key: str) -> MainSkillExtractionResult:
    with pool().connection() as conn:
        row = conn.execute("""
            select
                coalesce(enriched.title_translated, fact.title) as title,
                payload #>> '{category,key}' as main_skill
            from silver.fact_job as fact
            join bronze.raw_jobs as raw on raw.id = fact.bronze_id
            join ops.sites as sites on sites.id = raw.site_id
            left join ops.enriched_jobs as enriched on enriched.job_key = fact.job_key
            where sites.name = %s
            and fact.job_key = %s
            limit 1
        """, (SITE_NAME, job_key,)).fetchone()
        
        if row is None:
            return MainSkillExtractionResult()
        
        skills = inference(row[0])
        main_skill = None if len(skills) == 0 else skills[0]
        
        return MainSkillExtractionResult(
            site_suggested=row[1],
            nlp_suggested=main_skill,
        )