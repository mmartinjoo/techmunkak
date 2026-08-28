from techmunkak.embed import selectors
from techmunkak.embed.models import JobTranslationResult
from techmunkak.embed.services.translation import translate as trans

SITE_NAME="NoFluffJobs"

def need_translation(job_key: str) -> bool:
    payload = selectors.fetch_raw_job_payload(job_key=job_key)
        
    daily_tasks_lang = payload.get("metadata", {}).get("sectionLanguages", {}).get("daily-tasks")
    description_lang = payload.get("metadata", {}).get("sectionLanguages", {}).get("description")
    requirements_lang = payload.get("metadata", {}).get("sectionLanguages", {}).get("requirements.description")
    
    return daily_tasks_lang != "en" or description_lang != "en" or requirements_lang != "en"

def translate(job_key: str) -> JobTranslationResult:
    job = selectors.fetch_job_details_for_translation(job_key=job_key)
    title = trans.translate(text=job.title)
    description = trans.translate(text=job.description)
    
    return JobTranslationResult(
        title=title.translated_text,
        description=description.translated_text,
    )