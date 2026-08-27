{{ config(materialized='table') }}

with 
	seniorities as (
		select
			{{ dim_key('aliases.canonical_name', 'jobs.seniority') }} as seniority_key,
			coalesce(aliases.canonical_name, jobs.seniority) as name
		from {{ ref('int_jobs') }} jobs
		left join {{ ref('seniority_aliases') }} aliases
		on aliases.raw_value = lower(jobs.seniority)	
	)

select 
	seniority_key, 
	min(name) as name
from seniorities
group by seniority_key
