select
    url,    
    coalesce(salary #>> '{types,b2b,range,0}', salary #>> '{types,permanent,range,0}')::numeric as bottom,
    coalesce(salary #>> '{types,b2b,range,1}', salary #>> '{types,permanent,range,1}')::numeric as top,
    lower(coalesce(salary #>> '{types,b2b,period}', salary #>> '{types,permanent,period}')) as period,
    salary #>> '{currency}' as currency,
    case
        when salary #>> '{types,b2b}' is not null then  'b2b'
        else                                            'permanent'
    end as contract_type
from {{ ref('stg_nofluffjobs__jobs') }}
order by url