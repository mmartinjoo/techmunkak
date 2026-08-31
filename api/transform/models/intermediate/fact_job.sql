{{ config(materialized='table') }}

select
    jobs.job_key,
	jobs.title,
	jobs.description,
	jobs.posted_at,
	jobs.expires_at,
	jobs.url,
	jobs.monthly_salary_bottom,
	jobs.monthly_salary_top,
	jobs.currency_code,
    c.company_key as company_key,
    s.seniority_key as seniority_key,
    ct.contract_type_key as contract_type_key,
	country.country_key as country_key,
	jobs.bronze_id as bronze_id
from {{ ref('int_accepted_jobs') }} as jobs
left join {{ ref('dim_company') }} as c on {{ slug('c.name') }} = {{ slug('jobs.company_name') }}
left join {{ ref('seniority_aliases') }} as sa on sa.raw_value = lower(jobs.seniority)
left join {{ ref('dim_seniority') }} as s on s.name = sa.canonical_name
left join {{ ref('contract_type_aliases') }} as cta on cta.raw_value = lower(jobs.contract_type)
left join {{ ref('dim_contract_type') }} as ct on ct.name = cta.canonical_name
left join {{ ref('country_aliases') }} as cnta on cnta.code = lower(jobs.country_code)
left join {{ ref('dim_country') }} as country on country.name = cnta.name