from datetime import date

from techmunkak.core.db import pool

from techmunkak.api.schemas import LeaderboardMonthly

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