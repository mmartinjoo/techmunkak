create table if not exists bronze.raw_jobs(
    id serial primary key,
    site_id int references ops.sites(id),
    scrape_run_id int references ops.scrape_runs(id),
    job_url_id int references bronze.job_urls(id),
    payload jsonb not null
)