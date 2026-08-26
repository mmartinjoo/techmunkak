{{ config(materialized='table') }}

with 
	nofluffjobs_seniorities as (
		select
			distinct lower(coalesce(sa.canonical_name, j.seniority)) as seniority_key,
			coalesce(sa.canonical_name, j.seniority) as name
		from {{ ref('stg_nofluffjobs__jobs') }} j
		left join {{ ref('seniority_aliases') }} sa
		on sa.raw_value = lower(j.seniority)	
	),
	
	justjoinit_seniorities as (
		select
			distinct lower(coalesce(sa.canonical_name, j.experience_level)) as seniority_key,
			coalesce(sa.canonical_name, j.experience_level) as name
		from {{ ref('stg_justjoinit__jobs') }} j
		left join {{ ref('seniority_aliases') }} sa
		on sa.raw_value = lower(j.experience_level)	
	)

select * from nofluffjobs_seniorities
union
select * from justjoinit_seniorities
