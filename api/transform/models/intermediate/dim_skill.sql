{{ config(materialized='table') }}

with 
	names as (
		select
			sc.skill_key as skill_key,
			coalesce(sa.canonical_name, sc.name) as name
		from {{ ref('int_skill_candidates') }} as sc
		left join {{ ref('skill_aliases') }} as sa on sc.name = sa.raw_value
	)

select
	skill_key,
	name,
	{{ slug('name') }} as slug
from names