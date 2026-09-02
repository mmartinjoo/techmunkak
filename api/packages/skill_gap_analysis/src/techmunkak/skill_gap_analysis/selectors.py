import logging
from techmunkak.core.db import pool
from techmunkak.skill_gap_analysis.models import Job, Skill

logger = logging.getLogger(__name__)

def find_jobs(job_keys: list[str]) -> list[Job]:
    in_clause = ','.join(['%s'] * len(job_keys))
    with pool().connection() as conn:
        rows = conn.execute(f"""
            select
                fact.job_key,
                fact.title,
                fact.description,
                array_agg(
                    json_build_object('skill_key',skill.skill_key,'name',skill."name")
                ) as skills
            from silver.fact_job as fact                 
            join silver.job_skills as jskill on jskill.job_key = fact.job_key
            join silver.dim_skill as skill on skill.skill_key = jskill.skill_key
            where fact.job_key in ({in_clause})
            and jskill.required = true
            group by 1, 2, 3
        """, tuple(job_keys)).fetchall()
        
        if len(job_keys) != len(rows):
            logger.warning(f"find_jobs: got {len(job_keys)} job keys, queried {len(rows)} rows")
            logger.warning(f"find_jobs: job_keys: {job_keys}")
            logger.warning(f"find_jobs: rows: {[r[0] for r in rows]}")
        
        jobs = []
        for row in rows:
            jobs.append(Job(
                job_key=row[0],
                title=row[1],
                description=row[2],
                skills=[Skill(skill_key=s["skill_key"], name=s["name"]) for s in row[3]],
            ))                

        return jobs