from techmunkak.core.db import pool
from techmunkak.embed.models import MainSkillExtractionResult
from techmunkak.nlp.services.inference import inference

SITE_NAME = "JustJoinIT"

def extract(job_key: str) -> MainSkillExtractionResult:
    with pool().connection() as conn:
        row = conn.execute("""
            select
                enrichment.title_en as title,
                raw.payload #>> '{category,key}' as main_skill
            from silver.fact_job as fact
            join bronze.raw_jobs as raw on raw.id = fact.bronze_id
            join ops.sites as sites on sites.id = raw.site_id
            join ops.enrichment_results as enrichment on enrichment.job_key = fact.job_key
            where sites.name = %s
            and fact.job_key = %s
            limit 1
        """, (SITE_NAME, job_key,)).fetchone()
        
        if row is None:
            raise ValueError(f"job_key ({job_key}) not found for main skill extraction")
        
        if row[0] is None:
            raise ValueError(f"job ({job_key}) is not translated yet")
        
        skills = inference(row[0])
        main_skill = None if len(skills) == 0 else skills[0]
        
        if main_skill is None:
            skill = conn.execute("""
                select skill.name
                from silver.fact_job as fact
                join silver.job_skills as jskill on jskill.job_key = fact.job_key
                join silver.dim_skill as skill on skill.skill_key = jskill.skill_key
                where fact.job_key = %s
                limit 1
            """, (job_key,)).fetchone()
            
            if skill is not None:
                main_skill = skill[0]
        
        return MainSkillExtractionResult(
            site_suggested=row[1],
            nlp_suggested=main_skill,
        )