select 
    url as url,
    payload #>> '{title}' as title,
    payload #>> '{body}' as body,
    (payload #>> '{expiredAt}')::timestamptz as expires_at,
    payload #>> '{companyName}' as company_name,
    payload #>> '{companySize}' as company_size,
    payload #>> '{countryCode}' as country_code,
    (payload #>> '{publishedAt}')::timestamptz as published_at,
    payload #>> '{requiredSkills}' as required_skills,
    payload #>> '{niceToHaveSkills}' as nice_to_have_skills,
    payload #>> '{experienceLevel}' as experience_level,
    payload #>> '{employmentTypes}' as employement_types
from {{ source('bronze', 'raw_jobs') }} as rj
join ops.sites as s on rj.site_id = s.id
where s.name = '{{ var('site_identifier_justjoinit') }}'