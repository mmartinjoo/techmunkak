select *
from {{ ref('int_job_versions') }}
where version = 1