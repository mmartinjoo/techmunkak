{{ config(materialized='table') }}

select
    job_key,
    title as title_en,
    description as description_en,
    '' as main_skill_site_suggested,
    '' as main_skill_nlp_suggested,
    null::jsonb as chroma_embedding_ids,
    now() as created_at
from {{ ref('fact_job') }}