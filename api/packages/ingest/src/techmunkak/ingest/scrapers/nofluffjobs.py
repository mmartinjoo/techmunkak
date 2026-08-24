import requests
from techmunkak.ingest.models import SiteSearchTerm

def discover(site_search_term: SiteSearchTerm) -> list[dict]:
    assert "payload" in site_search_term.params, f"'payload' is missing from site search term params: {site_search_term}"
    assert "query" in site_search_term.params, f"'query' is missing from site search term params: {site_search_term}"
    
    assert "salaryPeriod" in site_search_term.params["query"], f"'query.salaryPeriod' is missing from site search term params: {site_search_term}"
    assert "salaryCurrency" in site_search_term.params["query"], f"'query.salaryCurrency' is missing from site search term params: {site_search_term}"
    
    assert "requirement" in site_search_term.params["payload"] or "rawSearch" in site_search_term.params["payload"], f"'payload.requirement' or 'payload.rawSearch' is missing from site search term params: {site_search_term}"    

    salary_period = site_search_term.params["query"]["salaryPeriod"]
    salary_currency = site_search_term.params["query"]["salaryCurrency"]
    
    request_payload = {}

    if "requirement" in site_search_term.params["payload"]:
        requirements = site_search_term.params["payload"]["requirement"]
        assert isinstance(requirements, list) and len(requirements) > 0, f"'payload.requirement' must be a list with at least one element: {site_search_term}"

        request_payload = {
            "criteriaSearch": {
                "requirement": requirements,
            },
        }
    else:
        raw_search = site_search_term.params["payload"]["rawSearch"]
        assert isinstance(raw_search, str) and len(raw_search) > 0, f"'payload.rawSearch' must be a search str: {site_search_term}"

        request_payload = {
            "rawSearch": raw_search,
        }

    page = 1
    limit = 20
    pages = []
    
    while page <= 5:
        url = f"https://nofluffjobs.com/api/search/posting?page={page}&limit={limit}&salaryCurrency={salary_currency}&salaryPeriod={salary_period}"
        
        resp = requests.post(
            url=url,
            json=request_payload,
            headers={
                "User-Agent": "insomnia/13.1.0",
            },
        )
        
        resp.raise_for_status()
        pages.append(resp.json())
        page += 1
        
    return pages