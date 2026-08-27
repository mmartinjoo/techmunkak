{{ config(materialized='table') }}

with 
	nofluffjobs_countries as (
		select
			{{ dim_key('ca.code', 'j.region') }} as country_key,
			coalesce(ca.name, j.region) as name
		from {{ ref('int_nofluffjobs__job_regions') }} j
		left join {{ ref('country_aliases') }} ca
		on ca.code = lower(j.region)	
	),
	
	justjoinit_countries as (
		select
			{{ dim_key('ca.code', 'j.country_code') }} as country_key,
			coalesce(ca.name, j.country_code) as name
		from {{ ref('stg_justjoinit__jobs') }} j
		left join {{ ref('country_aliases') }} ca
		on ca.code = lower(j.country_code)	
	)

select country_key, min(name) as name
from (
	select * from nofluffjobs_countries
	union all
	select * from justjoinit_countries
)
group by country_key