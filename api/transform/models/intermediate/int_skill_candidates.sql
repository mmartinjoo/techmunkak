with 
	required_skill_names as (
		select jsonb_array_elements(required_skills)->>0 as name
		from {{ ref('int_jobs') }}
	),

	optional_skill_names as (
		select jsonb_array_elements(optional_skills)->>0 as name
		from {{ ref('int_jobs') }}
	),
	
	skill_keys as (
		select 
			{{ slug('name') }} as skill_key,
			name
		from (
			select * from required_skill_names
			union all
			select * from optional_skill_names
		)
	)
	
select 
	md5(skill_key) as skill_key, 
	min(name) as name
from skill_keys
where skill_key is not null
group by skill_key