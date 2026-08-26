{{ config(materialized='table') }}

with
	nofluffjobs_jobs as (
		select
			j.url,
			j.title,
			concat_ws(' ', j.daily_tasks, j.description, j.requirements) as description,
			s.bottom as monthly_salary_bottom,
			s.top as monthly_salary_top,
			s.currency as currency
		from {{ ref('stg_nofluffjobs__jobs') }} as j
		join {{ ref('int_nofluffjobs__job_salaries') }} as s
		on j.url = s.url
	),
	
	justjoinit_jobs as (
		select
			j.url,
			j.title,
			j.body as description,
			s.bottom as monthly_salary_bottom,
			s.top as monthly_salary_top,
			s.currency as currency
		from {{ ref('stg_justjoinit__jobs') }} as j
		join {{ ref('int_justjoinit__job_salaries') }} as s
		on j.url = s.url
	)
	
select * from nofluffjobs_jobs
union
select * from justjoinit_jobs