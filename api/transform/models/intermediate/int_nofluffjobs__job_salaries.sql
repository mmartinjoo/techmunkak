select
    url,    
    coalesce(salary #>> '{types,b2b,range,0}', salary #>> '{types,permanent,range,0}') as bottom,
    coalesce(salary #>> '{types,b2b,range,1}', salary #>> '{types,permanent,range,1}') as top,
    lower(coalesce(salary #>> '{types,b2b,period}', salary #>> '{types,permanent,period}')) as period,
    salary #>> '{currency}' as currency
from {{ ref('stg_nofluffjobs__jobs') }}
order by url