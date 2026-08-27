with 
	nofluffjobs_required_skills as (
		select
			external_id,
			jsonb_agg(skill) as skills
		from
			(select
				external_id,
				jsonb_array_elements(must_have_skills) #>> '{value}' as skill
			from {{ ref('stg_nofluffjobs__jobs') }})
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
			from {{ ref('stg_nofluffjobs__jobs') }})
		group by external_id
	),
	
	nofluffjobs_salaries as (
		select
		    external_id,        
		    case
		        when lower(coalesce(salary #>> '{types,b2b,period}', salary #>> '{types,permanent,period}')) = 'hour' then coalesce(salary #>> '{types,b2b,range,0}', salary #>> '{types,permanent,range,0}')::numeric * 168
		        when lower(coalesce(salary #>> '{types,b2b,period}', salary #>> '{types,permanent,period}')) = 'day' then coalesce(salary #>> '{types,b2b,range,0}', salary #>> '{types,permanent,range,0}')::numeric * 21
		        else coalesce(salary #>> '{types,b2b,range,0}', salary #>> '{types,permanent,range,0}')::numeric
		    end as bottom,
		    case
		        when lower(coalesce(salary #>> '{types,b2b,period}', salary #>> '{types,permanent,period}')) = 'hour' then coalesce(salary #>> '{types,b2b,range,1}', salary #>> '{types,permanent,range,1}')::numeric * 168
		        when lower(coalesce(salary #>> '{types,b2b,period}', salary #>> '{types,permanent,period}')) = 'day' then coalesce(salary #>> '{types,b2b,range,1}', salary #>> '{types,permanent,range,1}')::numeric * 21
		        else coalesce(salary #>> '{types,b2b,range,1}', salary #>> '{types,permanent,range,1}')::numeric
		    end as top,
		    'month' as period,
		    upper((salary #>> '{currency}')::text) as currency_code,
		    case
		        when salary #>> '{types,b2b}' is not null then  'b2b'
		        else                                            'permanent'
		    end as contract_type
		from {{ ref('stg_nofluffjobs__jobs') }}
	),
	
	justjointit_employement_types as (
		select
			external_id,
			jsonb_array_elements(employement_types) as employment_type
		from {{ ref('stg_justjoinit__jobs') }}
	),
	
	justjointit_employement_types_eur as (
		select
			*,
			row_number() over (
				partition by external_id
			) as version
		from justjointit_employement_types
		where employment_type #>> '{currency}' = 'EUR'	
	),
	
	justjoinit_salaries as (
		select 
			external_id,
			(employment_type #>> '{from}')::numeric as bottom,
			(employment_type #>> '{to}')::numeric as top,
			'month' as period,
			'EUR' as currency_code,
			employment_type #>> '{type}' as contract_type
		from justjointit_employement_types_eur
		where version = 1
	),
	
	justjoinit_required_skills as (
		select
			external_id,
			jsonb_agg(skill) as skills
		from
			(select
				external_id,
				jsonb_array_elements(required_skills) #>> '{name}' as skill
			from {{ ref('stg_justjoinit__jobs') }})
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
			from {{ ref('stg_justjoinit__jobs') }})
		group by external_id
	),
	
	nofluffjobs_jobs as (
		select			
			md5(jobs.site_id || md5(jobs.url)) as job_key,
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
			salaries.bottom as monthly_salary_bottom,
			salaries.top as monthly_salary_top,
			salaries.period as salary_period,
			salaries.currency_code as currency_code,
			salaries.contract_type as contract_type,
			jobs.url,
			md5(url) as url_hash
		from {{ ref('stg_nofluffjobs__jobs') }} as jobs
		left join nofluffjobs_required_skills as required_skills on required_skills.external_id = jobs.external_id
		left join nofluffjobs_optional_skills as optional_skills on optional_skills.external_id = jobs.external_id
		left join nofluffjobs_salaries as salaries on salaries.external_id = jobs.external_id	
	),
	
	justjoinit_jobs as (
		select			
			md5(jobs.site_id || md5(jobs.url)) as job_key,
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
			md5(jobs.url) as url_hash
		from {{ ref('stg_justjoinit__jobs') }} as jobs
		left join justjoinit_required_skills as required_skills on required_skills.external_id = jobs.external_id
		left join justjoinit_optional_skills as optional_skills on optional_skills.external_id = jobs.external_id
		left join justjoinit_salaries as salaries on salaries.external_id = jobs.external_id	
	)
	
select * from justjoinit_jobs
union all
select * from nofluffjobs_jobs