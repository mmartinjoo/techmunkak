select     
    case        
        when monthly_salary_bottom is null or monthly_salary_top is null then 'monthly_salary_missing'
        when monthly_salary_bottom <= 100 or monthly_salary_bottom >= 100000 then 'monthly_salary_bottom_out_of_range'
        when monthly_salary_top <= 100 or monthly_salary_top >= 100000 then 'monthly_salary_top_out_of_range'
        when salary_period != 'month' then 'salary_period_mismatch'
        when currency_code != 'EUR' then 'currency_mismatch'        
    end as reason,
    *
from {{ ref('int_jobs') }}
where monthly_salary_bottom is null 
or monthly_salary_top is null
or monthly_salary_bottom <= 100
or monthly_salary_top <= 100
or monthly_salary_bottom >= 100000
or monthly_salary_top >= 100000
or currency_code != 'EUR'
or salary_period != 'month'