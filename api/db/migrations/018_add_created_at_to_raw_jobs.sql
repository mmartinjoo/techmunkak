alter table bronze.raw_jobs
add column created_at timestamptz default now();