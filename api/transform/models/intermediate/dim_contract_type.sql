{{ config(materialized='table') }}

with 
	contract_types as (
		select
			{{ dim_key('aliases.canonical_name', 'jobs.contract_type') }} as contract_type_key,
			coalesce(aliases.canonical_name, jobs.contract_type) as name
		from {{ ref('int_jobs') }} jobs
		left join {{ ref('contract_type_aliases') }} aliases
		on aliases.raw_value = lower(jobs.contract_type)	
	)

select 
	contract_type_key, 
	min(name) as name
from contract_types
group by contract_type_key
