import logging
from datetime import date, datetime

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from techmunkak.api import selectors, services
from techmunkak.core.config import settings
from techmunkak.core.logging import setup_logging
from techmunkak.cv_match.run import match_cv as cv_matcher

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
    query = selectors.LeaderboardQuery(
        month=month,
        skill_key=skill_key,
        country_key=country_key,
        seniority_key=seniority_key,
    )
    
    return query.execute()

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
        parts = file.filename.split(".")
        base_name = "temp" if len(parts) != 2 else parts[0]
        filename = f"{base_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf"
        key = services.upload_cv_to_s3(filename=filename, contents=contents)
        job_keys = cv_matcher(cv_s3_key=key)
        return selectors.find_jobs(job_keys=job_keys)
    except Exception:
        logger.exception("CV matching failed")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong",
        )
        
def main():
    setup_logging()
    uvicorn.run(
        "techmunkak.api.run:app",
        host="0.0.0.0",
        port=80,
        reload=True if settings.environment == 'local' else False,
    )