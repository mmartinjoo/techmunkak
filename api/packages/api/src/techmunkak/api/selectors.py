from datetime import date
import logging

from techmunkak.core.db import pool

from techmunkak.api.schemas import Job, LeaderboardMonthly, MostPopularMainSkillByMonth, MostPopularSkillByMonth, TopPayingMainSkillByMonth, TopPayingSkillByMonth, Skill

logger = logging.getLogger(__name__)

class LeaderboardQuery():
    month: date 
    skill_key: str | None = None
    country_key: str | None = None
    seniority_key: str | None = None
    
    variables: list[str]
    
    def __init__(
        self,
        month: date,
        skill_key: str | None = None,
        country_key: str | None = None,
        seniority_key: str | None = None,
    ):
        self.month = month
        self.skill_key = skill_key
        self.country_key = country_key
        self.seniority_key = seniority_key
        self.variables = []
    
    def execute(self) -> list[LeaderboardMonthly]:
        sql = self.get_skill_aggregation_cte()
        sql += self.get_base_query()
        sql += self.get_filters()
        sql += self.get_group_by()
        
        with pool().connection() as conn:
            rows = conn.execute(sql, self.variables).fetchall()
            
            return [LeaderboardMonthly(
                month=r[0], 
                median_monthly_salary_bottom=r[1],
                median_monthly_salary_top=r[2],
                count=r[3],
            ) 
            for r in rows]
    
    def get_skill_aggregation_cte(self):
        sql = """
            with
                skills_agg as (
                    select
                        jskill.job_key,
                        array_agg(skill.name) skills
                    from silver.dim_skill as skill
                    join silver.job_skills as jskill on jskill.skill_key = skill.skill_key		
        """
        
        if self.skill_key:
            self.variables.append(self.skill_key)
            sql = sql + """
                where skill.skill_key = %s
                group by jskill.job_key
            )
            """
        else:
            sql = sql + """
                group by jskill.job_key
            )
            """
            
        return sql
            
    def get_base_query(self):
        return """
            \n
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
        """
    
    def get_filters(self):
        self.variables.append(self.month)
        sql = "where date_trunc('month', fact.posted_at) = %s"
        
        if self.seniority_key:
            self.variables.append(self.seniority_key)
            sql += """
                \nand seniority.seniority_key = %s
            """
            
        if self.country_key:
            self.variables.append(self.country_key)
            sql += """
                \nand country.country_key = %s
            """
        
        return sql
    
    def get_group_by(self):
        return """
            group by 1
            order by count desc
        """
        
def fetch_most_popular_main_skills_by_month(start_month: date, end_month: date) -> list[MostPopularMainSkillByMonth]:
    with pool().connection() as conn:
        rows = conn.execute("""
            select month, main_skill, count
            from gold.most_popular_main_skills_by_month
            where month between %s and %s
            order by count desc
        """, (start_month, end_month,)).fetchall()
        
        return [
            MostPopularMainSkillByMonth(
                month=r[0],
                skill=r[1],
                count=r[2],
            )
            for r in rows
        ]
        
def fetch_most_popular_skills_by_month(start_month: date, end_month: date) -> list[MostPopularMainSkillByMonth]:
    with pool().connection() as conn:
        rows = conn.execute("""
            select month, skill.skill_key, skill.name, count
            from gold.most_popular_skills_by_month as mart
            join silver.dim_skill as skill on skill.skill_key = mart.skill_key
            where month between %s and %s
            order by count desc
        """, (start_month, end_month,)).fetchall()
        
        return [
            MostPopularSkillByMonth(
                month=r[0],
                skill_key=r[1],
                skill_name=r[2],
                count=r[3],
            )
            for r in rows
        ]
        
def fetch_top_paying_main_skills_by_month(start_month: date, end_month: date) -> list[TopPayingMainSkillByMonth]:
    with pool().connection() as conn:
        rows = conn.execute("""
            select month, main_skill, median_monthly_salary_bottom, median_monthly_salary_top
            from gold.top_paying_main_skills_by_month
            where month between %s and %s
            order by median_monthly_salary_top desc
        """, (start_month, end_month,)).fetchall()
        
        return [
            TopPayingMainSkillByMonth(
                month=r[0],
                skill=r[1],
                median_monthly_salary_bottom=r[2],
                median_monthly_salary_top=r[3],
            )
            for r in rows
        ]
        
def fetch_top_paying_skills_by_month(start_month: date, end_month: date) -> list[TopPayingSkillByMonth]:
    with pool().connection() as conn:
        rows = conn.execute("""
            select month, skill.skill_key, skill.name, median_monthly_salary_bottom, median_monthly_salary_top
            from gold.top_paying_skills_by_month as mart
            join silver.dim_skill as skill on skill.skill_key = mart.skill_key
            where month between %s and %s
            order by median_monthly_salary_top desc
        """, (start_month, end_month,)).fetchall()
        
        return [
            TopPayingSkillByMonth(
                month=r[0],
                skill_key=r[1],
                skill_name=r[2],
                median_monthly_salary_bottom=r[3],
                median_monthly_salary_top=r[4],
            )
            for r in rows
        ]
        
def find_jobs(job_keys: list[str]) -> list[Job]:
    in_clause = ','.join(['%s'] * len(job_keys))
    with pool().connection() as conn:
        rows = conn.execute(f"""
            select
                fact.job_key,
                fact.title,
                array_agg(
                    json_build_object('skill_key',skill.skill_key,'name',skill."name")
                ) as skills
            from silver.fact_job as fact                 
            join silver.job_skills as jskill on jskill.job_key = fact.job_key
            join silver.dim_skill as skill on skill.skill_key = jskill.skill_key
            where fact.job_key in ({in_clause})
            and jskill.required = true
            group by 1, 2
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
                skills=[Skill(skill_key=s["skill_key"], name=s["name"]) for s in row[2]]
            ))                

        return jobs