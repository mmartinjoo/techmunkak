alter table bronze.job_urls
drop column status;

alter table bronze.job_urls
drop column error;

alter table bronze.job_urls
drop column attempts;

alter table bronze.job_urls
drop column next_attempt_at;