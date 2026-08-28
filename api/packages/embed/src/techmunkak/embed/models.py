from dataclasses import dataclass


@dataclass
class JobTranslationResult():
    title: str
    description: str
   
@dataclass 
class Job():
    job_key: str
    site_name: str