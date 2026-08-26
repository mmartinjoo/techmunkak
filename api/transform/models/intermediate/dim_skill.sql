{{ config(materialized='table') }}

select
	sc.name,
	coalesce(sa.canonical_name, sc.canonical_name) as canonical_name,
	md5(sc.name) as skill_key	
from {{ ref('int_skill_candidates') }} as sc
left join {{ ref('skill_aliases') }} as sa on sc.name = sa.raw_value