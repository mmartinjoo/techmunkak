import requests
from techmunkak.ingest.models import SiteSearchTerm

SITE_NAME = "JustJoinIT"

def fetch_search_result_pages(site_search_term: SiteSearchTerm, max_pages: int = 5, per_page_limit: int = 10) -> list[dict]:
    """
    Fetches X pages of the search results for a given search term. Returns the raw JSON as a dict
    """
    pages = []
    page = 1
    while page <= max_pages:
        items_from = (page - 1) * per_page_limit
        url = f"https://justjoin.it/api/candidate-api/offers?from={items_from}&itemsCount={per_page_limit}&keyword={site_search_term.search_term.term}"
        
        resp = requests.get(
            url=url,
            headers={
                "User-Agent": "insomnia/13.1.0",
                "Accept": "application/json",
            },
        )
        
        resp.raise_for_status()
        pages.append(resp.json())
        page += 1
        
    return pages

def parse_job_urls(search_result_page_data: dict) -> list[str]:
    """
    Parses all job listing URLs from a search result page JSON
    """
    
    assert "data" in search_result_page_data, f"'data' key missing from search result page data: {search_result_page_data}"
    
    return [f"https://justjoin.it/api/candidate-api/offers/{item['slug']}" for item in search_result_page_data["data"]]

def dedupe_job_urls(job_urls: list[str]) -> list[str]:
    return job_urls

def fetch_job_details(url: str) -> dict:
    resp = requests.get(
        url=url,
        headers={
            "User-Agent": "insomnia/13.1.0",
            "Accept": "application/json",
        },
    )
    
    resp.raise_for_status()
    
    return resp.json()

def get_site_name() -> str:
    return SITE_NAME