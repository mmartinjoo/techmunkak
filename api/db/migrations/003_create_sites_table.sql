create table if not exists ops.sites(
    id serial primary key,
    name text,
    base_url text,
    is_active boolean,
    created_at timestamptz default now()
)