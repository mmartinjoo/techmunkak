{{ config(materialized='table') }}

with 
	names as (
		select
			sc.skill_key as skill_key,
			coalesce(sa.canonical_name, sc.name) as name,
			black.name as black
		from {{ ref('int_skill_candidates') }} as sc
		left join {{ ref('skill_aliases') }} as sa on sc.name = sa.raw_value
		left join {{ ref('blacklisted_skills') }} as black on {{ slug('black.name') }} = {{ slug_with_coalesce('sa.canonical_name', 'sc.name') }}
		where black.name is null
	)

select
	skill_key,
	name,
	regexp_replace(lower(btrim(name)), '\W', '-', 1, 0, 'i') as slug
from names