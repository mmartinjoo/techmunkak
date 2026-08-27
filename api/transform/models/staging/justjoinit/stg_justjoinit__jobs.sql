select 
    payload #>> '{id}' as external_id,
    payload #>> '{title}' as title,    
    payload #>> '{body}' as body,    
    (payload #>> '{publishedAt}')::timestamptz as posted_at,
    coalesce(
        (payload #>> '{expiredAt}')::timestamptz,
        (payload #>> '{publishedAt}')::timestamptz + interval '1 month'
    ) as expires_at,
    payload #>> '{companyName}' as company_name,
    payload #>> '{companySize}' as company_size,
    payload #>> '{countryCode}' as country_code,
    (payload #>> '{publishedAt}')::timestamptz as published_at,
    (payload #>> '{requiredSkills}')::jsonb as required_skills,
    (payload #>> '{niceToHaveSkills}')::jsonb as nice_to_have_skills,
    payload #>> '{experienceLevel}' as experience_level,
    (payload #>> '{employmentTypes}')::jsonb as employement_types,
    url as url,
    site_id as site_id,
    fetched_at::timestamptz as fetched_at,
    rj.id as bronze_id
from {{ source('bronze', 'raw_jobs') }} as rj
join ops.sites as s on rj.site_id = s.id
where s.name = '{{ var('site_identifier_justjoinit') }}'