select 
    {{ dbt_utils.star(ref('int_job_versions'), except=["version", "monthly_salary_bottom", "monthly_salary_top", "currency_code"]) }},
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
from {{ ref('int_job_versions') }} as jobs
left join {{ source('bronze', 'currency_conversions') }} as conversions on conversions.from_currency_code = jobs.currency_code
where version = 1