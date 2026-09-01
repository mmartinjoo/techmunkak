select *
from {{ ref('int_jobs') }}
where monthly_salary_bottom is not null
and monthly_salary_top is not null
and monthly_salary_bottom > {{ var('monthly_salary_min') }}
and monthly_salary_top > {{ var('monthly_salary_min') }}
and monthly_salary_bottom < {{ var('monthly_salary_max') }}
and monthly_salary_top < {{ var('monthly_salary_max') }}
and currency_code = 'EUR'
and salary_period = 'month'