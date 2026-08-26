with
    nofluffjobs_skills as (
        select distinct lower(btrim(skill, ' ')) as skill,
        regexp_replace(lower(btrim(skill, ' ')), '\W', '-', 1, 0, 'i') as key
        from {{ ref('int_nofluffjobs__job_skills') }}
    ),

    justjoinit_skills as (
        select distinct lower(btrim(skill, ' ')) as skill,
        regexp_replace(lower(btrim(skill, ' ')), '\W', '-', 1, 0, 'i') as key
        from {{ ref('int_justjoinit__job_skills') }}
    )

select skill, key from nofluffjobs_skills
union
select skill, key from justjoinit_skills
order by skill