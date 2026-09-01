select 
	date_trunc('month', fact.posted_at)::date as month,
	enriched.main_skill as main_skill,
	(percentile_cont(0.5) within group (
		order by fact.monthly_salary_bottom desc
	))::int as median_monthly_salary_bottom,
	(percentile_cont(0.5) within group (
		order by fact.monthly_salary_top desc
	))::int as median_monthly_salary_top
from {{ ref('fact_job') }} as fact
join {{ ref('int_enriched_jobs') }} as enriched on enriched.job_key = fact.job_key
group by 1, 2
order by median_monthly_salary_top desc
limit 10