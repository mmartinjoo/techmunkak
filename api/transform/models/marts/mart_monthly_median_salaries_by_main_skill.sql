{{ config(materialized='table') }}

select
	date_trunc('month', fact.posted_at)::date as month,
	count(*),
	enriched.main_skill,
	percentile_cont(0.5) within group (
		order by monthly_salary_bottom
	) as median_monthly_salary_bottom,
	percentile_cont(0.5) within group (
		order by monthly_salary_top
	) as median_monthly_salary_top
from {{ ref('fact_job') }} as fact
join {{ ref('int_enriched_jobs') }} as enriched on enriched.job_key = fact.job_key
group by date_trunc('month', posted_at)::date, main_skill
having count(*) > 5
order by count desc