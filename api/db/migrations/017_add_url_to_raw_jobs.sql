alter table bronze.raw_jobs
add column url text not null;

create unique index site_id_url_unique on bronze.raw_jobs (site_id, url);