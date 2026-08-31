from dataclasses import dataclass
from typing import Protocol

from techmunkak.enrich.models import MainSkillExtractionResult
from techmunkak.enrich.services.main_skill_extraction import nofluffjobs, justjoinit

MAIN_SKILL_EXTRACTORS = {
    nofluffjobs.SITE_NAME: nofluffjobs,
    justjoinit.SITE_NAME: justjoinit,
}

class MainSkillExtractor(Protocol):
    def extract(job_key: str) -> MainSkillExtractionResult: ...
    
def get_main_skill_extractor(site_name: str) -> MainSkillExtractor:
    try:
        return MAIN_SKILL_EXTRACTORS[site_name]
    except KeyError:
        raise ValueError(f"unknown site for skill extractor: {site_name}")