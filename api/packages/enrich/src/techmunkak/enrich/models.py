from dataclasses import dataclass


@dataclass
class JobTranslationResult():
    title: str
    description: str
   
@dataclass 
class Job():
    job_key: str
    site_name: str
    
@dataclass 
class EmbeddableJob():
    job_key: str
    content: str
    
@dataclass
class MainSkillExtractionResult():
    site_suggested: str | None = None
    nlp_suggested: str | None = None