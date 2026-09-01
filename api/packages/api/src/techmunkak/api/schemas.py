from dataclasses import dataclass
from datetime import date


@dataclass
class LeaderboardMonthly():
    month: date
    median_monthly_salary_bottom: int
    median_monthly_salary_top: int
    count: int
    
@dataclass
class MostPopularSkillByMonth():
    month: date
    skill: str
    count: int
    
@dataclass
class TopPayingSkillByMonth():
    month: date
    skill: str
    median_monthly_salary_bottom: int
    median_monthly_salary_top: int