select 
	date_trunc('month', job.posted_at)::date as month,
	skill.skill_key,
	(percentile_cont(0.5) within group (
		order by job.monthly_salary_bottom desc
	))::int as median_monthly_salary_bottom,
	(percentile_cont(0.5) within group (
		order by job.monthly_salary_top desc
	))::int as median_monthly_salary_top
from {{ ref('dim_skill') }} as skill
join {{ ref('job_skills') }} as jskill on jskill.skill_key = skill.skill_key
join {{ ref('fact_job') }} as job on job.job_key = jskill.job_key
group by 1, 2
order by median_monthly_salary_top desc
limit 50