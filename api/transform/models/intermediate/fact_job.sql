{{ config(materialized='table') }}

select
    jobs.job_key,
	jobs.title,
	jobs.description,
	jobs.posted_at,
	jobs.expires_at,
	jobs.url,
    c.company_key as company_key,
    s.seniority_key as seniority_key,
    ct.contract_type_key as contract_type_key,
	country.country_key as country_key,
	(case
		when conversions.value > 1.0 then jobs.monthly_salary_bottom / conversions.value
		when conversions.value < 1.0 then jobs.monthly_salary_bottom * conversions.value
		when conversions.value = 1.0 then jobs.monthly_salary_bottom
		else 							  jobs.monthly_salary_bottom
	end)::int as monthly_salary_bottom,
	(case
		when conversions.value > 1.0 then jobs.monthly_salary_top / conversions.value
		when conversions.value < 1.0 then jobs.monthly_salary_top * conversions.value
		when conversions.value = 1.0 then jobs.monthly_salary_top
		else 							  jobs.monthly_salary_top
	end)::int as monthly_salary_top,
	coalesce(conversions.to_currency_code, jobs.currency_code) as currency_code
from {{ ref('int_jobs') }} as jobs
left join {{ ref('dim_company') }} as c on c.name = jobs.company_name
left join {{ ref('seniority_aliases') }} as sa on sa.raw_value = lower(jobs.seniority)
left join {{ ref('dim_seniority') }} as s on s.name = sa.canonical_name
left join {{ ref('contract_type_aliases') }} as cta on cta.raw_value = lower(jobs.contract_type)
left join {{ ref('dim_contract_type') }} as ct on ct.name = cta.canonical_name
left join {{ ref('country_aliases') }} as cnta on cnta.code = lower(jobs.country_code)
left join {{ ref('dim_country') }} as country on country.name = cnta.name
left join {{ source('bronze', 'currency_conversions') }} as conversions on conversions.from_currency_code = jobs.currency_code