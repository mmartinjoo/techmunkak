create table if not exists ops.embedded_jobs(
    id serial primary key,
    job_key text not null unique,
    chroma_ids jsonb not null,
    created_at timestamptz not null default now()
)