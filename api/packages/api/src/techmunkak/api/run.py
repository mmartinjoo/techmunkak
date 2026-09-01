import uvicorn
from datetime import date
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from techmunkak.core.config import settings

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

def main():
    uvicorn.run(
        "techmunkak.api.run:app",
        host="0.0.0.0",
        port=80,
        reload=True if settings.environment == 'local' else False,
    )