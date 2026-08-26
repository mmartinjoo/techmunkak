{{ config(materialized='table') }}

with
	job_skills as (
		select * from {{ ref('int_nofluffjobs__job_skills') }}
		union
		select * from {{ ref('int_justjoinit__job_skills') }}
	)
	
select 
	js.url,
	coalesce(sa.canonical_name, js.skill) as canonical_name,
	js.required
from job_skills as js
left join {{ ref('skill_aliases') }} as sa
on sa.raw_value = lower(btrim(js.skill))