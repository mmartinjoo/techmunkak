select
    url,        
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
    upper((salary #>> '{currency}')::text) as currency,
    case
        when salary #>> '{types,b2b}' is not null then  'b2b'
        else                                            'permanent'
    end as contract_type
from {{ ref('stg_nofluffjobs__jobs') }}
order by url