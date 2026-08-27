{{ config(materialized='table') }}

with 
	nofluffjobs_seniorities as (
		select
			{{ dim_key('sa.canonical_name', 'j.seniority') }} as seniority_key,
			coalesce(sa.canonical_name, j.seniority) as name
		from {{ ref('stg_nofluffjobs__jobs') }} j
		left join {{ ref('seniority_aliases') }} sa
		on sa.raw_value = lower(j.seniority)	
	),
	
	justjoinit_seniorities as (
		select
			{{ dim_key('sa.canonical_name', 'j.experience_level') }} as seniority_key,
			coalesce(sa.canonical_name, j.experience_level) as name
		from {{ ref('stg_justjoinit__jobs') }} j
		left join {{ ref('seniority_aliases') }} sa
		on sa.raw_value = lower(j.experience_level)	
	)

select seniority_key, min(name) as name
from (
	select seniority_key, name from nofluffjobs_seniorities
	union all
	select seniority_key, name from justjoinit_seniorities
)
group by seniority_key
