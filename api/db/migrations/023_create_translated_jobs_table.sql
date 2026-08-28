create table if not exists ops.translated_jobs(
    id serial primary key,
    job_key text not null unique,
    title_translated text not null,
    description_translated text not null,
    created_at timestamptz not null default now()
)