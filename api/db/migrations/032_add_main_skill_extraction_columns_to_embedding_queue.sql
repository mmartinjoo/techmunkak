alter table ops.embedding_queue
add column main_skill_extracted boolean not null default false;

alter table ops.embedding_queue
add column main_skill_extracted_at timestamptz default null;