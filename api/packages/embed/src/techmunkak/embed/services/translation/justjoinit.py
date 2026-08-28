from langdetect import detect, DetectorFactory
from techmunkak.embed import selectors
from techmunkak.embed.models import Job
from techmunkak.embed.services.translation import translate as trans

SITE_NAME="JustJoinIT"

def need_translation(job_key: str) -> bool:
    payload = selectors.fetch_raw_job_payload(job_key=job_key)
        
    DetectorFactory.seed = 0
    lang = detect(text=payload["body"])
    
    return lang != "en"    

def translate(job_key: str) -> dict:
    job = selectors.fetch_job_details_for_translation(job_key=job_key)
    title = trans.translate(text=job.title)
    description = trans.translate(text=job.description)
    
    return Job(
        title=title.translated_text,
        description=description.translated_text,
    )