create table if not exists ops.cv_matching_results(
    id serial primary key,
    cv_s3_key text not null,
    job_keys jsonb not null,
    created_at timestamptz not null default now()
)