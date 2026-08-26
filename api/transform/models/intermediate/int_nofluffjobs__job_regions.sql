select
    url,    
    jsonb_array_elements(regions)->>0 as region
from {{ ref('stg_nofluffjobs__jobs') }}
order by url