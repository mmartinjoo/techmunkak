from typing import Protocol

from techmunkak.ingest.models import SiteSearchTerm
from techmunkak.ingest.scrapers import nofluffjobs, justjoinit

class Scraper(Protocol):
    def fetch_search_result_pages(site_search_term: SiteSearchTerm, max_pages: int = 5, per_page_limit: int = 10) -> list[dict]: ...
    def parse_job_urls(search_result_page_data: dict) -> list[str]: ...
    def dedupe_job_urls(job_urls: list[str]) -> list[str]: ...
    def fetch_job_details(url: str) -> dict: ...
    def get_site_name(): str: ...

SCRAPERS: dict[str, Scraper] = {
    nofluffjobs.SITE_NAME: nofluffjobs,
    justjoinit.SITE_NAME: justjoinit,
}

def get_scraper(site_name: str):
    try:
        return SCRAPERS[site_name]
    except KeyError:
        raise ValueError(f"no scraper for: {site_name}")