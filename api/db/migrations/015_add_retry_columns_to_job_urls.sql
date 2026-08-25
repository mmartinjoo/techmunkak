alter table bronze.job_urls
add column attempts int default 0;

alter table bronze.job_urls
add column next_attempt_at timestamptz default now();