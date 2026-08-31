{{ config(materialized='table') }}

with
	required_skills as (
		select 
			job_key,
			jsonb_array_elements(required_skills)->>0 as skill,
			true as required
		from {{ ref('int_accepted_jobs') }}
	),
	
	optional_skills as (
		select 
			job_key,
			jsonb_array_elements(optional_skills)->>0 as skill,
			false as required
		from {{ ref('int_accepted_jobs') }}
	),
	
	skills as (
		select * from required_skills
		union all
		select * from optional_skills
	)
	
select 
	skills.job_key,
	dim.skill_key,
	skills.required
from skills as skills
left join {{ ref('dim_skill') }} as dim on dim.slug = {{ slug('skills.skill') }}