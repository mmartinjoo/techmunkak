with
	raw_must_have_skills as (
		select
			url,
			jsonb_array_elements(required_skills) #>> '{name}' as skill,
			True as required
		from {{ ref('stg_justjoinit__jobs') }}
	),
	
	raw_nice_to_have_skills as (
		select
			url,
			jsonb_array_elements(nice_to_have_skills) #>> '{name}' as skill,
			False as required
		from {{ ref('stg_justjoinit__jobs') }}
	)
	
select * from raw_must_have_skills 
union all
select * from raw_nice_to_have_skills
order by url