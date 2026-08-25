create table if not exists bronze.jobs(
    id serial primary key,
    site_id int references ops.sites(id),
    url text not null,
    title text not null,
    created_at timestamptz default now()
)