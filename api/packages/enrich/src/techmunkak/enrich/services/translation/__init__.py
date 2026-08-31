from typing import Protocol

from techmunkak.enrich.models import JobTranslationResult
from techmunkak.enrich.services.translation import nofluffjobs, justjoinit


class Translator(Protocol):
    def need_translation(job_key: str) -> bool: ...
    def translate(job_key: str) -> JobTranslationResult: ...
    
TRANSLATORS = {
    nofluffjobs.SITE_NAME: nofluffjobs,
    justjoinit.SITE_NAME: justjoinit,
}
    
def get_translator(site_name: str) -> Translator:
    try:
        return TRANSLATORS[site_name]
    except Exception:
        raise KeyError(f"invalid translator: {site_name}")