from langdetect import detect, DetectorFactory
from techmunkak.embed import selectors

SITE_NAME="JustJoinIT"

def need_translation(job_key: str) -> bool:
    payload = selectors.fetch_raw_job_payload(job_key=job_key)
        
    DetectorFactory.seed = 0
    lang = detect(text=payload["body"])
    
    return lang != "en"    