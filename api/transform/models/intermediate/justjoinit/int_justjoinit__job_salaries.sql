with
	employment_types as (
		select
			url,
			jsonb_array_elements(employement_types) as employment_type
		from {{ ref('stg_justjoinit__jobs') }}
	),
	
	employment_type_eur as (
		select *
		from employment_types
		where employment_type #>> '{currency}' = 'EUR'	
	)
	
select 
	url,
	(employment_type #>> '{from}')::numeric as bottom,
	(employment_type #>> '{to}')::numeric as top,
	'month' as period,
	'EUR' as currency,
	employment_type #>> '{type}' as contract_type
from employment_type_eur