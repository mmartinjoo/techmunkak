{{ config(materialized='table') }}

select
    fact.job_key as job_key,
    enrichment.title_en as title,
    enrichment.description_en as description,
    coalesce(enrichment.main_skill_nlp_suggested, enrichment.main_skill_site_suggested) as main_skill,
    enrichment.chroma_embedding_ids,
    now() as created_at
from {{ ref('fact_job') }} as fact
join {{ source('ops', 'enrichment_results') }} as enrichment on enrichment.job_key = fact.job_key
where enrichment.ready = true