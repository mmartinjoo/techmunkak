from dataclasses import dataclass
from datetime import date


@dataclass
class LeaderboardMonthly():
    month: date
    median_monthly_salary_bottom: int
    median_monthly_salary_top: int
    count: int
    
@dataclass
class MostPopularMainSkillByMonth():
    month: date
    skill: str
    count: int
    
@dataclass
class TopPayingMainSkillByMonth():
    month: date
    skill: str
    median_monthly_salary_bottom: int
    median_monthly_salary_top: int
    
@dataclass
class MostPopularSkillByMonth():
    month: date
    skill_key: str
    skill_name: str
    count: int
    
@dataclass
class TopPayingSkillByMonth():
    month: date
    skill_key: str
    skill_name: str
    median_monthly_salary_bottom: int
    median_monthly_salary_top: int

@dataclass
class Skill():
    skill_key: str
    name: str
    
@dataclass
class Job():
    job_key: str
    title: str
    skills: list[Skill]