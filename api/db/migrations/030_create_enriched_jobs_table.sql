create table if not exists ops.enriched_jobs(
    id serial primary key,
    job_key text not null unique,
    title_translated text default null,
    description_translated text default null,
    chroma_embedding_ids jsonb default null,
    main_skill text default null,
    created_at timestamptz not null default now()
)