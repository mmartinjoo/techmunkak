select 
    {{ dbt_utils.star(ref('int_job_versions'), except=["version"]) }}
from {{ ref('int_job_versions') }}
where version = 1