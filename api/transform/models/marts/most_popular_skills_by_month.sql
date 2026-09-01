select 
	date_trunc('month', job.posted_at)::date as month,
	skill.skill_key,
	count(jskill.job_key)
from {{ ref('dim_skill') }} as skill
join {{ ref('job_skills') }} as jskill on jskill.skill_key = skill.skill_key
join {{ ref('fact_job') }} as job on job.job_key = jskill.job_key
group by 1, 2
having count(jskill.job_key) > {{ var('min_coccurrence_to_be_top_kill') }}
order by count(jskill.job_key) desc
limit {{ var('top_skills_limit') }}