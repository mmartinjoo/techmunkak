from datetime import date

from techmunkak.core.db import pool

from techmunkak.api.schemas import Leaderboard


def fetch_leaderboard(
    month: date, 
    skill_key: str | None = None,
    country_key: str | None = None,
    seniority_key: str | None = None,
) -> list[Leaderboard]:
    with pool().connection() as conn:
        rows = conn.execute("""
            with
                skills_agg as (
                    select
                        jskill.job_key,
                        array_agg(skill.name) skills
                    from silver.dim_skill as skill
                    join silver.job_skills as jskill on jskill.skill_key = skill.skill_key		
                    where skill.skill_key = %s
                    group by jskill.job_key
                )

            select
                date_trunc('month', fact.posted_at)::date as month,
                (percentile_cont(0.5) within group (
                    order by fact.monthly_salary_bottom
                ))::int as median_monthly_salary_bottom,
                (percentile_cont(0.5) within group (
                    order by fact.monthly_salary_top
                ))::int as median_monthly_salary_top,
                count(fact.job_key) as count
            from silver.fact_job as fact
            join silver.dim_country as country on country.country_key = fact.country_key
            join silver.dim_seniority as seniority on seniority.seniority_key = fact.seniority_key
            join skills_agg as skills on skills.job_key = fact.job_key
            where date_trunc('month', fact.posted_at) = %s
            and country.country_key = %s
            and seniority.seniority_key = %s
            group by 1
            order by count desc
        """, (
            skill_key, 
            month,
            country_key,
            seniority_key,
        )).fetchall()
        
        return [Leaderboard(
            month=r[0], 
            median_monthly_salary_bottom=r[1],
            median_monthly_salary_top=r[2],
            count=r[3],
        ) 
        for r in rows]