select 
  url as url,
  payload->>'title' as title,
  (payload #>> '{specs, dailyTasks}')::jsonb as daily_tasks,
  payload #>> '{basics, category}' as category,
  payload #>> '{basics, seniority}' as seniority,
  payload #>> '{basics, technology}' as technology,
  (payload['posted']::bigint/1000)::int as posted_at,
  nullif(payload #>> '{company, url}', '') as company_url,
  payload #>> '{company, name}' as company_name,
  payload #>> '{company, size}' as company_size,
  payload #>> '{details, description}' as description,
  nullif(payload #>> '{details, position}', '') as position,
  (payload->>'regions')::jsonb as regions,
  (payload->>'expiresAt')::timestamptz as expires_at,
  (payload #>> '{requirements, musts}')::jsonb as must_have_skills,
  (payload #>> '{requirements, nices}')::jsonb as nice_to_have_skills,
  payload #>> '{requirements, description}' as requirements,
  (payload #>> '{essentials, originalSalary}')::jsonb as salary
from {{ source('bronze', 'raw_jobs') }} as rj
join ops.sites as s on rj.site_id = s.id
where s.name = '{{ var('site_identifier_nofluffjobs') }}'