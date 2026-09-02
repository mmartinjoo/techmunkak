create table if not exists ops.cache(
    id serial primary key,
    key text not null unique,
    value jsonb not null unique,
    created_at timestamptz not null default now(),
    expires_at timestamptz not null default now() + interval '10 minutes'
)