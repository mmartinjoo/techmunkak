{{ config(materialized='table') }}

with 
	nofluffjobs_contract_types as (
		select
			distinct lower(coalesce(cta.canonical_name, s.contract_type)) as contract_type_key,
			coalesce(cta.canonical_name, s.contract_type) as name
		from {{ ref('int_nofluffjobs__job_salaries') }} s
		left join {{ ref('contract_type_aliases') }} cta
		on cta.raw_value = lower(s.contract_type)	
	),
	
	justjoinit_contract_types as (
		select
			distinct lower(coalesce(cta.canonical_name, s.contract_type)) as contract_type_key,
			coalesce(cta.canonical_name, s.contract_type) as name
		from {{ ref('int_justjoinit__job_salaries') }} s
		left join {{ ref('contract_type_aliases') }} cta
		on cta.raw_value = lower(s.contract_type)	
	)

select * from nofluffjobs_contract_types
union
select * from justjoinit_contract_types
