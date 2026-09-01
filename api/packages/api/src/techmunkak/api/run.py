from itertools import count

import uvicorn
from datetime import date
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from techmunkak.core.config import settings
from techmunkak.api import selectors

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

def main():
    uvicorn.run(
        "techmunkak.api.run:app",
        host="0.0.0.0",
        port=80,
        reload=True if settings.environment == 'local' else False,
    )