import logging
from datetime import date, datetime, timedelta

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from techmunkak.api import selectors, services
from techmunkak.core.config import settings
from techmunkak.core.logging import setup_logging
from techmunkak.cv_match.run import match_cv as cv_matcher
from techmunkak.cv_match.services import cv_parser
from techmunkak.core import cache
from techmunkak.embeddings.services import embedder, vector_store
from techmunkak.skill_gap_analysis.services import analyze_skill_gap

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/ping")
def market_months():
    return "ok"

@app.get("/api/leaderboard")
def leaderboard(
    month: date,
    skill_key: str | None = None,
    country_key: str | None = None,
    seniority_key: str | None = None,
):
    key = cache.key(month=month, skill_key=skill_key, country_key=country_key, seniority_key=seniority_key)
    if cache.has(key):
        value = cache.get(key)
        if value is not None:
            return value
    
    query = selectors.LeaderboardQuery(
        month=month,
        skill_key=skill_key,
        country_key=country_key,
        seniority_key=seniority_key,
    )
    
    value = query.execute()
    cache.set(key, value, expires_at=datetime.now() + timedelta(hours=1))
    
    return value

@app.get("/api/most-popular-main-skills")
def most_popular_main_skills(start_month: date, end_month: date):
    return selectors.fetch_most_popular_main_skills_by_month(
        start_month=start_month,
        end_month=end_month,
    )
    
@app.get("/api/most-popular-skills")
def most_popular_skills(start_month: date, end_month: date):
    return selectors.fetch_most_popular_skills_by_month(
        start_month=start_month,
        end_month=end_month,
    )
    
@app.get("/api/top-paying-main-skills")
def top_paying_main_skills(start_month: date, end_month: date):
    return selectors.fetch_top_paying_main_skills_by_month(
        start_month=start_month,
        end_month=end_month,
    )
    
@app.get("/api/top-paying-skills")
def top_paying_skills(start_month: date, end_month: date):
    return selectors.fetch_top_paying_skills_by_month(
        start_month=start_month,
        end_month=end_month,
    )
    
@app.post("/api/match-cv")
async def match_cv(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    try:        
        contents = await file.read()
        filename = services.get_name_for_uploaded_cv(file.filename)
        key = services.upload_cv_to_s3(filename=filename, contents=contents)
        job_keys = cv_matcher(cv_s3_key=key)
        services.create_cv_matching_result(cv_s3_key=key, job_keys=list(job_keys))
        return selectors.find_jobs(job_keys=job_keys)
    except Exception:
        logger.exception("CV matching failed")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong",
        )
        
@app.post("/api/skill-gap-analysis")
async def skill_gap_analysis(
    file: UploadFile = File(...),
    target_role: str = Form(min_length=3),
):
    if not file.filename.endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )
        
    try:        
        contents = await file.read()
        filename = services.get_name_for_uploaded_cv(file.filename)
        key = services.upload_cv_to_s3(filename=filename, contents=contents)
        cv_content = cv_parser.parse(cv_s3_key=key)
        embedding = embedder.embed(content=target_role)
        job_keys = vector_store.query_jobs_by_embedding(embedding=embedding, k=10)
        return analyze_skill_gap(cv_content=cv_content, target_role=target_role, target_job_keys=job_keys)
    except Exception:
        logger.exception("skill gap analysis failed")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong",
        )
        
@app.get('/api/test')
def test():
    cache.evict()
    
        
def main():
    setup_logging()
    uvicorn.run(
        "techmunkak.api.run:app",
        host="0.0.0.0",
        port=80,
        reload=True if settings.environment == 'local' else False,
    )