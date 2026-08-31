from techmunkak.core.db import pool
from techmunkak.enrich.models import MainSkillExtractionResult

SITE_NAME = "NoFluffJobs"

def extract(job_key: str) -> MainSkillExtractionResult:
    with pool().connection() as conn:
        row = conn.execute("""
            select
                raw.payload #>> '{basics, technology}' as main_skill
            from silver.fact_job as fact
            join bronze.raw_jobs as raw on raw.id = fact.bronze_id
            join ops.sites as sites on sites.id = raw.site_id
            where sites.name = %s
            and fact.job_key = %s
            limit 1
        """, (SITE_NAME, job_key,)).fetchone()
        
        if row is None:
            raise ValueError(f"job_key ({job_key}) not found for main skill extraction")
        
        return MainSkillExtractionResult(
            site_suggested=row[0],
            nlp_suggested=None,
        )