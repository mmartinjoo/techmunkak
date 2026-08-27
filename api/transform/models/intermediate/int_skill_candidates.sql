with
    nofluffjobs_skills as (
        select
            skill as name,
            {{ slug('skill') }} as skill_key
        from {{ ref('int_nofluffjobs__job_skills') }}
    ),

    justjoinit_skills as (
        select
            skill as name,
            {{ slug('skill') }} as skill_key
        from {{ ref('int_justjoinit__job_skills') }}
    )

select md5(skill_key) as skill_key, min(name) as name
from (
    select * from nofluffjobs_skills
    union all
    select * from justjoinit_skills
)
group by skill_key