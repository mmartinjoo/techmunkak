create table if not exists ops.scrape_runs(
    id serial primary key,
    site_id int references ops.sites(id),
    search_term_id int references ops.search_terms(id),
    started_at timestamptz not null default now(),
    finished_at timestamptz default null,
    status text default 'pending',
    discovered_count int default 0
)