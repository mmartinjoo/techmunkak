select *
from {{ ref('int_jobs') }}
where monthly_salary_bottom is not null
and monthly_salary_top is not null
and monthly_salary_bottom > 100
and monthly_salary_top > 100
and monthly_salary_bottom < 100000
and monthly_salary_top < 100000
and currency_code = 'EUR'
and salary_period = 'month'