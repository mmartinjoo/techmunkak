from datetime import datetime
from typing import Optional, TypeAlias

from pydantic import BaseModel, Field

class Site(BaseModel):
    id: int
    name: str = Field(min_length=5, max_length=100)
    base_url: str = Field(min_length=5, max_length=100)
    is_active: bool = True
    created_at: datetime
    
class SearchTerm(BaseModel):
    id: int
    term: str
    is_active: bool = True
    priority: int = Field(gt=0, lt=101, default=100)
    created_at: datetime
    
class SiteSearchTerm(BaseModel):
    id: int
    params: dict
    last_run_at: Optional[datetime] = Field(default=None)
    site: Site
    search_term: SearchTerm
    importance_score: Optional[float] = Field(gt=0, lt=10.1, default=None)
    
class ScrapeRun(BaseModel):
    id: int
    site: Site
    search_term: SearchTerm
    started_at: datetime
    finished_at: Optional[datetime] = Field(default=None)
    status: str
    
class JobUrl(BaseModel):
    id: int
    scrape_run: ScrapeRun
    site: Site
    url: str
    url_hash: str
    first_seen_at: datetime
    last_fetched_at: Optional[datetime] = Field(default=None)
    status: str
    s3_key: Optional[str] = Field(default=None)