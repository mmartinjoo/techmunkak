create table if not exists ops.ingestion_queue(
    id serial primary key,
    job_url_id int references bronze.job_urls(id),
    attempts int not null default 0,
    next_attempt_at timestamptz not null default now(),
    fetched boolean not null default false,
    loaded boolean not null default false,
    status text not null default 'waiting_for_fetching',
    error text default null,
    discovered_at timestamptz not null default now(),
    fetched_at timestamptz not null default now(),
    loaded_at timestamptz not null default now(),
    created_at timestamptz not null default now()
)