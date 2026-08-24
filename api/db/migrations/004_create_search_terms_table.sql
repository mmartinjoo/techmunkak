create table if not exists ops.search_terms(
    id serial primary key,
    term text,
    is_active boolean,
    priority int default 100 check (priority between 1 and 100),
    created_at timestamptz default now()
)