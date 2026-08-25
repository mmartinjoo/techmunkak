create table if not exists bronze.job_urls(
    id serial primary key,
    scrape_run_id int references ops.scrape_runs(id),
    site_id int references ops.sites(id),
    url text not null,
    url_hash text not null,
    first_seen_at timestamptz not null default now(),
    last_fetched_at timestamptz default null,
    status text not null default 'pending',
    error text default null,
    s3_key text default null,
    unique(site_id, url_hash)
)