create table if not exists ops.site_search_terms(
    id serial primary key,
    site_id bigint references ops.sites(id),
    search_term_id bigint references ops.search_terms(id),
    params jsonb not null,
    last_run_at timestamptz,
    constraint unique_site_search_term unique(site_id, search_term_id)
)