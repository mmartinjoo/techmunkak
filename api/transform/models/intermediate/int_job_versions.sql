with 
	nofluffjobs_jobs_deduped as (
		select *
		from (
			select 
				*,
				row_number() over (
					partition by external_id
					order by fetched_at desc, bronze_id desc
				) as version
			from {{ ref('stg_nofluffjobs__jobs') }}
		) as jobs
		where version = 1
	),

	nofluffjobs_required_skills as (
		select
			external_id,
			jsonb_agg(skill) as skills
		from
			(select
				external_id,
				jsonb_array_elements(must_have_skills) #>> '{value}' as skill
			from nofluffjobs_jobs_deduped)
		group by external_id
	),

	nofluffjobs_optional_skills as (
		select
			external_id,
			jsonb_agg(skill) as skills
		from
			(select
				external_id,
				jsonb_array_elements(nice_to_have_skills) #>> '{value}' as skill
			from nofluffjobs_jobs_deduped)
		group by external_id
	),

	nofluffjobs_b2b_salaries as (
		select
		    external_id,        
		    (case
				when salary #>> '{types,b2b,range,0}' is null 			then null
				when lower(salary #>> '{types,b2b,period}') = 'hour' 	then (salary #>> '{types,b2b,range,0}')::numeric * 168
				when lower(salary #>> '{types,b2b,period}') = 'day' 	then (salary #>> '{types,b2b,range,0}')::numeric * 21
				else	 													 (salary #>> '{types,b2b,range,0}')::numeric
		    end)::int as bottom,
		    (case
		        when salary #>> '{types,b2b,range,1}' is null 			then null
				when lower(salary #>> '{types,b2b,period}') = 'hour' 	then (salary #>> '{types,b2b,range,1}')::numeric * 168
				when lower(salary #>> '{types,b2b,period}') = 'day' 	then (salary #>> '{types,b2b,range,1}')::numeric * 21
				else	 													 (salary #>> '{types,b2b,range,1}')::numeric
		    end)::int as top,
		    'month' as period,
		    upper((salary #>> '{currency}')::text) as currency_code,
		    'b2b' as contract_type
		from nofluffjobs_jobs_deduped
	),

	nofluffjobs_permanent_salaries as (
		select
		    external_id,        
		    (case
				when salary #>> '{types,permanent,range,0}' is null 			then null
				when lower(salary #>> '{types,permanent,period}') = 'hour' 		then (salary #>> '{types,permanent,range,0}')::numeric * 168
				when lower(salary #>> '{types,permanent,period}') = 'day' 		then (salary #>> '{types,permanent,range,0}')::numeric * 21
				else	 													 		 (salary #>> '{types,permanent,range,0}')::numeric
		    end)::int as bottom,
		    (case
		        when salary #>> '{types,permanent,range,1}' is null 			then null
				when lower(salary #>> '{types,permanent,period}') = 'hour' 		then (salary #>> '{types,permanent,range,1}')::numeric * 168
				when lower(salary #>> '{types,permanent,period}') = 'day' 		then (salary #>> '{types,permanent,range,1}')::numeric * 21
				else	 													 		 (salary #>> '{types,permanent,range,1}')::numeric
		    end)::int as top,
		    'month' as period,
		    upper((salary #>> '{currency}')::text) as currency_code,
		    'permanent' as contract_type
		from nofluffjobs_jobs_deduped
	),
	
	justjoinit_jobs_deduped as (
		select *
		from (
			select *,
				row_number() over (
					partition by external_id
					order by fetched_at desc, bronze_id desc
				) as version
			from {{ ref('stg_justjoinit__jobs') }}
		) as jobs
		where version = 1
	),
	
	justjointit_employement_types as (
		select
			external_id,
			jsonb_array_elements(employement_types) as employment_type
		from justjoinit_jobs_deduped
	),
	
	justjointit_employement_types_eur as (
		select *
		from justjointit_employement_types
		where employment_type #>> '{currency}' = 'EUR'	
	),
	
	justjoinit_salaries as (
		select 
			external_id,
			(case
				when lower(employment_type #>> '{unit}') = 'hour' then (employment_type #>> '{fromPerUnit}')::numeric * 168
				when lower(employment_type #>> '{unit}') = 'day'  then (employment_type #>> '{fromPerUnit}')::numeric * 21
				else (employment_type #>> '{fromPerUnit}')::numeric
			end)::int as bottom,
			(case
				when lower(employment_type #>> '{unit}') = 'hour' then (employment_type #>> '{toPerUnit}')::numeric * 168
				when lower(employment_type #>> '{unit}') = 'day'  then (employment_type #>> '{toPerUnit}')::numeric * 21
				else (employment_type #>> '{toPerUnit}')::numeric
			end)::int as top,
			'month' as period,
			'EUR' as currency_code,
			employment_type #>> '{type}' as contract_type
		from justjointit_employement_types_eur
	),
	
	justjoinit_required_skills as (
		select
			external_id,
			jsonb_agg(skill) as skills
		from
			(select
				external_id,
				jsonb_array_elements(required_skills) #>> '{name}' as skill
			from justjoinit_jobs_deduped)
		group by external_id
	),

	justjoinit_optional_skills as (
		select
			external_id,
			jsonb_agg(skill) as skills
		from
			(select
				external_id,
				jsonb_array_elements(nice_to_have_skills) #>> '{name}' as skill
			from justjoinit_jobs_deduped)
		group by external_id
	),
	
	nofluffjobs_jobs as (
		select			
			case
				when b2b_salaries.external_id is not null then md5(concat_ws('||', jobs.site_id::text, jobs.url, b2b_salaries.contract_type))
				else md5(concat_ws('||', jobs.site_id::text, jobs.url, permanent_salaries.contract_type))
			end as job_key,			
			jobs.title,
			concat_ws(' ', jobs.daily_tasks, jobs.description, jobs.requirements) as description,
			jobs.company_name as company_name,
			jobs.company_size as company_size,
			jobs.seniority as seniority,
			jsonb_array_elements(regions)->>0 as country_code,
			jobs.posted_at as posted_at,
			jobs.expires_at as expires_at,			
			required_skills.skills as required_skills,
			optional_skills.skills as optional_skills,
			case
				when b2b_salaries.bottom is not null then b2b_salaries.bottom
				else permanent_salaries.bottom
			end as monthly_salary_bottom,
			case
				when b2b_salaries.top is not null then b2b_salaries.top
				else permanent_salaries.top
			end as monthly_salary_top,
			case
				when b2b_salaries.period is not null then b2b_salaries.period
				else permanent_salaries.period
			end as salary_period,
			case
				when b2b_salaries.currency_code is not null then b2b_salaries.currency_code
				else permanent_salaries.currency_code
			end as currency_code,
			case
				when b2b_salaries.contract_type is not null then b2b_salaries.contract_type
				else permanent_salaries.contract_type
			end as contract_type,
			jobs.url,
			md5(url) as url_hash,
			jobs.version as version
		from nofluffjobs_jobs_deduped as jobs
		left join nofluffjobs_required_skills as required_skills on required_skills.external_id = jobs.external_id
		left join nofluffjobs_optional_skills as optional_skills on optional_skills.external_id = jobs.external_id
		left join nofluffjobs_b2b_salaries as b2b_salaries on b2b_salaries.external_id = jobs.external_id	
		left join nofluffjobs_permanent_salaries as permanent_salaries on permanent_salaries.external_id = jobs.external_id	
	),
	
	justjoinit_jobs as (
		select			
			md5(concat_ws('||', jobs.site_id::text, jobs.url, salaries.contract_type)) as job_key,
			jobs.title,
			jobs.body as description,
			jobs.company_name as company_name,
			jobs.company_size as company_size,
			jobs.experience_level as seniority,
			jobs.country_code as country_code,
			jobs.posted_at as posted_at,
			jobs.expires_at as expires_at,
			required_skills.skills as required_skills,
			optional_skills.skills as optional_skills,
			salaries.bottom as monthly_salary_bottom,
			salaries.top as monthly_salary_top,
			salaries.period as salary_period,
			salaries.currency_code as currency_code,
			salaries.contract_type as contract_type,
			jobs.url,
			md5(jobs.url) as url_hash,
			jobs.version as version
		from justjoinit_jobs_deduped as jobs
		left join justjoinit_required_skills as required_skills on required_skills.external_id = jobs.external_id
		left join justjoinit_optional_skills as optional_skills on optional_skills.external_id = jobs.external_id
		left join justjoinit_salaries as salaries on salaries.external_id = jobs.external_id	
	)
	
select * from justjoinit_jobs
union all
select * from nofluffjobs_jobs