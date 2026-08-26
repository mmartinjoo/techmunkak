alter table bronze.raw_jobs
add column url text not null;

create unique index url_unique on bronze.raw_jobs (url);