with
	raw_must_have_skills as (
		select
			url,
			jsonb_array_elements(must_have_skills) #>> '{value}' as skill,
			True as required
		from {{ ref('stg_nofluffjobs__jobs') }}
	),
	
	raw_nice_to_have_skills as (
		select
			url,
			jsonb_array_elements(nice_to_have_skills) #>> '{value}' as skill,
			False as required
		from {{ ref('stg_nofluffjobs__jobs') }}
	)
	
select * from raw_must_have_skills 
union 
select * from raw_nice_to_have_skills
order by url