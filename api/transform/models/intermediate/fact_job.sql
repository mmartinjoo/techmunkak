{{ config(materialized='table') }}

with
	nofluffjobs_jobs as (
		select
			j.url,
			j.title,
			concat_ws(' ', j.daily_tasks, j.description, j.requirements) as description,
			s.bottom as monthly_salary_bottom,
			s.top as monthly_salary_top,
			s.currency as currency,
            j.company_name as company_name,
			j.seniority as seniority,
			s.contract_type as contract_type,
			r.region as country_code
		from {{ ref('stg_nofluffjobs__jobs') }} as j
		left join {{ ref('int_nofluffjobs__job_salaries') }} as s on j.url = s.url
		left join {{ ref('int_nofluffjobs__job_regions') }} r on r.url = j.url
	),
	
	justjoinit_jobs as (
		select
			j.url,
			j.title,
			j.body as description,
			s.bottom as monthly_salary_bottom,
			s.top as monthly_salary_top,
			s.currency as currency,
            j.company_name as company_name,
			j.experience_level as seniority,
			s.contract_type as contract_type,
			j.country_code as country_code
		from {{ ref('stg_justjoinit__jobs') }} as j
		left join {{ ref('int_justjoinit__job_salaries') }} as s on j.url = s.url
	),

    jobs as (
        select * from nofluffjobs_jobs 
        union all 
        select * from justjoinit_jobs
    )
	
select
    j.url,
    j.title,
    j.description,
    j.monthly_salary_bottom,
    j.monthly_salary_top,
    j.currency,
    c.company_key as company_key,
    s.seniority_key as seniority_key,
    ct.contract_type_key as contract_type_key,
	country.country_key as country_key 
from jobs as j
left join {{ ref('dim_company') }} as c on c.name = j.company_name
left join {{ ref('seniority_aliases') }} as sa on sa.raw_value = lower(j.seniority)
left join {{ ref('dim_seniority') }} as s on s.name = sa.canonical_name
left join {{ ref('contract_type_aliases') }} as cta on cta.raw_value = lower(j.contract_type)
left join {{ ref('dim_contract_type') }} as ct on ct.name = cta.canonical_name
left join {{ ref('country_aliases') }} as cnta on cnta.code = lower(j.country_code)
left join {{ ref('dim_country') }} as country on country.name = cnta.name