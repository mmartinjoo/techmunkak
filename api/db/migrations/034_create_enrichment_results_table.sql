create table if not exists ops.enrichment_results(
    id serial primary key,
    job_key text not null unique,
    title_en text default null,
    description_en text default null,
    main_skill_site_suggested text default null,
    main_skill_nlp_suggested text default null,
    chroma_embedding_ids jsonb default null,
    ready boolean not null default false,
    created_at timestamptz not null default now()
)