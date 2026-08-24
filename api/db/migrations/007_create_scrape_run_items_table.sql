create table if not exists ops.scrape_run_items(
    id serial primary key,
    scrape_run_id int references ops.scrape_runs(id),
    site_id int references ops.sites(id),
    url text,
    url_hash text,
    first_seen_at timestamptz default now(),
    last_fetched_at timestamptz default null,
    unique(site_id, url_hash)
)