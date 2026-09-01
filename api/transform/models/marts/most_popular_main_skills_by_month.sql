select 
	date_trunc('month', fact.posted_at)::date as month,
	enriched.main_skill as main_skill,
	count(fact.job_key)
from {{ ref('fact_job') }} as fact
join {{ ref('int_enriched_jobs') }} as enriched on enriched.job_key = fact.job_key
group by 1, 2
having count(fact.*) > {{ var('min_coccurrence_to_be_top_kill') }}
order by count(fact.*) desc
limit {{ var('top_skills_limit') }}