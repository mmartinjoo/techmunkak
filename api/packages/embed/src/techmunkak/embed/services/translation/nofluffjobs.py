from techmunkak.embed import selectors

SITE_NAME="NoFluffJobs"

def need_translation(job_key: str) -> bool:
    payload = selectors.fetch_raw_job_payload(job_key=job_key)
        
    daily_tasks_lang = payload.get("metadata", {}).get("sectionLanguages", {}).get("daily-tasks")
    description_lang = payload.get("metadata", {}).get("sectionLanguages", {}).get("description")
    requirements_lang = payload.get("metadata", {}).get("sectionLanguages", {}).get("requirements.description")
    
    return daily_tasks_lang != "en" or description_lang != "en" or requirements_lang != "en"