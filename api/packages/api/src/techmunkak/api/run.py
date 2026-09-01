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
def leaderboard():
    return selectors.fetch_leaderboard(
        month=date.fromisoformat("2026-08-01"),
        skill_key="23eeeb4347bdd26bfc6b7ee9a3b755dd",
    )

def main():
    uvicorn.run(
        "techmunkak.api.run:app",
        host="0.0.0.0",
        port=80,
        reload=True if settings.environment == 'local' else False,
    )