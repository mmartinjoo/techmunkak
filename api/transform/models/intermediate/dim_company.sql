{{ config(materialized='table') }}

with 
	nofluffjobs_companies as (
		select 
			distinct company_name as name,
			company_size as size,
			md5({{ slug('company_name') }}) as company_key
		from {{ ref('stg_nofluffjobs__jobs') }}
	),
	
	justjoinit_companies as (
		select 
			distinct company_name as name,
			company_size as size,
			md5({{ slug('company_name') }}) as company_key
		from {{ ref('stg_justjoinit__jobs') }}
	)
	
select * from nofluffjobs_companies
union
select * from justjoinit_companies	