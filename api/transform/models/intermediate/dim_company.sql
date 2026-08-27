{{ config(materialized='table') }}

with 
	nofluffjobs_companies as (
		select 
			md5({{ slug('company_name') }}) as company_key,
			company_name as name,
			company_size as size
		from {{ ref('stg_nofluffjobs__jobs') }}
	),
	
	justjoinit_companies as (
		select 
			md5({{ slug('company_name') }}) as company_key,
			company_name as name,
			company_size as size
		from {{ ref('stg_justjoinit__jobs') }}
	)
	
select company_key, min(name) as name, nullif(min(size), '') as size
from (
	select * from nofluffjobs_companies
	union all
	select * from justjoinit_companies	
)
group by company_key