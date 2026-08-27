{{ config(materialized='table') }}

with 
	companies as (
		select 
			md5({{ slug('company_name') }}) as company_key,
			company_name as name,
			company_size as size
		from {{ ref('int_jobs') }}
	)

select 
	company_key, 
	min(name) as name, 
	nullif(min(size), '') as size
from companies
group by company_key