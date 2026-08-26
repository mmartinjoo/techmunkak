{{ config(materialized='table') }}

with 
	nofluffjobs_countries as (
		select
			distinct coalesce(ca.code, j.region) as country_key,
			ca.name
		from {{ ref('int_nofluffjobs__job_regions') }} j
		left join {{ ref('country_aliases') }} ca
		on ca.code = lower(j.region)	
	),
	
	justjoinit_countries as (
		select
			distinct coalesce(ca.code, j.country_code) as country_key,
			ca.name
		from {{ ref('stg_justjoinit__jobs') }} j
		left join {{ ref('country_aliases') }} ca
		on ca.code = lower(j.country_code)	
	)

select * from nofluffjobs_countries
union
select * from justjoinit_countries
