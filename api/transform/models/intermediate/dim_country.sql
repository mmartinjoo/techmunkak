{{ config(materialized='table') }}

with 
	countries as (
		select
			{{ dim_key('aliases.code', 'jobs.country_code') }} as country_key,
			coalesce(aliases.name, jobs.country_code) as name
		from {{ ref('int_jobs') }} jobs
		left join {{ ref('country_aliases') }} aliases
		on aliases.code = lower(jobs.country_code)	
	)

select country_key, min(name) as name
from countries
group by country_key