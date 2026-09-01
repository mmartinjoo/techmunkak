import io
from pypdf import PdfReader
import Levenshtein
import re
from techmunkak.core import storage
from techmunkak.core.db import pool
from techmunkak.skill_model.services.inference import inference as skill_model

def match(cv_s3_key: str) -> list[str]:
    content = parse_cv(cv_s3_key=cv_s3_key)
    skills = extract_skills_from_cv(cv_content=content)
    matches = find_matching_jobs(cv_skills=skills)
    normalized_matches = max_abs_normalizer(scores=matches)
    top_jobs = find_top_jobs(normalized_scores=normalized_matches)
    return top_jobs
    
def parse_cv(cv_s3_key: str) -> str:
    content = storage.get_pdf(cv_s3_key)
    buf = io.BytesIO(content)
    reader = PdfReader(buf)
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        replaced = text.replace("\n", "")
        texts.append(replaced)
        
    return "".join(texts)
    
def extract_skills_from_cv(cv_content: str) -> list[str]:
    skills = skill_model(text=cv_content)
    return skills

def find_matching_jobs(cv_skills: list[str]) -> dict[str, float]:
    with pool().connection() as conn:
        jobs = conn.execute("""
            select
                jskill.job_key,
                array_agg(lower(btrim(skill.name))) as skills	
            from silver.dim_skill as skill
            join silver.job_skills as jskill on jskill.skill_key = skill.skill_key
            group by jskill.job_key             
        """).fetchall()
        
        scores: dict[str, int] = {}
        for job_key, job_skills in jobs:
            score = 0
            for cv_skill in cv_skills:
                for job_skill in job_skills:
                    clean_job_skill = re.sub("\\d.+", "", job_skill)
                    clean_cv_skill = re.sub("\\d.+", "", cv_skill)
                    
                    if not clean_cv_skill:
                        clean_cv_skill = cv_skill
                    if not clean_job_skill:
                        clean_job_skill = job_skill
                    
                    clean_job_skill = clean_job_skill.strip()
                    clean_cv_skill = clean_cv_skill.strip()
                    
                    ratio = Levenshtein.ratio(clean_job_skill, clean_cv_skill)
                    
                    if ratio > 0.55:
                        score += ratio
                        
            scores[job_key] = score
            
        return scores
    
def max_abs_normalizer(scores: dict[str, float]) -> dict[str, float]:
    normalized_scores = {}
    max_score = sorted(scores.values(), reverse=True)[0]
    for job_key, score in scores.items():
        normalized_score = max(score / max_score, 0)
        normalized_scores[job_key] = normalized_score
    
    return normalized_scores
        
def find_top_jobs(normalized_scores: dict[str, float]) -> list[str]:
    top = {}
    for job_key, score in normalized_scores.items():
        if score >= 0.67:
            top[score] = job_key
    
    sorted_scores = sorted(top.keys(), reverse=True)
    top_jobs = []
    for score in sorted_scores:
        top_jobs.append(top[score])
        
    return top_jobs