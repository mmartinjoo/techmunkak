create table if not exists ops.embedding_queue(
    id serial primary key,
    job_key text not null unique,
    attempts int not null default 1,
    next_attempt_at timestamptz not null default now(),
    need_translation boolean not null default true,
    translated boolean not null default false,
    embedded boolean not null default false,
    status text not null default 'pending',
    error text default null,
    created_at timestamptz not null default now(),
    translated_at timestamptz default null,
    embedded_at timestamptz default null
)