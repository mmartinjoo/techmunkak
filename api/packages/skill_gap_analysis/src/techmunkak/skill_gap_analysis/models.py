from dataclasses import dataclass

@dataclass
class Skill():
    skill_key: str
    name: str

@dataclass
class Job():
    job_key: str
    title: str
    description: str
    skills: list[Skill]