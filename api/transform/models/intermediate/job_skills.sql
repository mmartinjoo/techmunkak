{{ config(materialized='table') }}

with
	all_job_skills as (
		select * from {{ ref('int_nofluffjobs__job_skills') }}
		union all
		select * from {{ ref('int_justjoinit__job_skills') }}
	)
	
select 
	js.url,
	s.skill_key,
	js.required
from all_job_skills as js
left join {{ ref('dim_skill') }} as s
on s.slug = {{ slug('js.skill') }}