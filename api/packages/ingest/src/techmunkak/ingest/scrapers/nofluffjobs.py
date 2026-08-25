import json
from datetime import datetime

import requests
import Levenshtein
from techmunkak.ingest.models import SiteSearchTerm
from techmunkak.core import storage
from techmunkak.ingest import selectors
from techmunkak.ingest.services import tracking

def discover(site_search_term: SiteSearchTerm, scrape_run_id: int) -> tuple[list[str], list[str]]:
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
    
    while page <= 1:
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
        
    jobs = []
    s3_keys = []
    for i, listing_page_data in enumerate(pages):
        key = storage.put_listing_page(
            site="NoFluffJobs",
            search_term=site_search_term.search_term.term,
            data=listing_page_data,
            page=i+1,
            scrape_run_id=scrape_run_id,
        )
        s3_keys.append(key)
        
        jobs.append(parse_job_urls(listing_page_data=listing_page_data))
        
    flat_job_urls = [item for sublist in jobs for item in sublist]
    
    root_urls = []
    
    url_groups: dict[str, list[str]] = {}
    already_grouped_urls: set[str] = set()
    
    for job_url in flat_job_urls:
        same_job_urls = find_same_job_urls(
            target_job_url=job_url,
            all_job_urls=flat_job_urls,
            already_grouped_urls=already_grouped_urls,
        )
        
        if same_job_urls is None:
            continue
        
        url_groups[job_url] = same_job_urls
        already_grouped_urls.add(job_url)
        for same_job_url in same_job_urls:
            already_grouped_urls.add(same_job_url)
        
        root_urls = []
        for target_job_url, similar_jobs_urls in url_groups.items():
            root_url = get_root_job_url(
                target_job_url=target_job_url, 
                similar_job_urls=similar_jobs_urls,
            )
            
            if root_url is None:
                continue
            
            root_urls.append(root_url)
        
    return (root_urls, s3_keys)

def fetch_job_details(job_url_id: int):
    job_url = selectors.find_job_url(id=job_url_id)
    
    resp = requests.get(
        url=f"https://nofluffjobs.com/api/posting/{job_url.url}",
        headers={
            "User-Agent": "insomnia/13.1.0",
        },
    )
    resp.raise_for_status()
    
    data = resp.json()
    
    key = storage.put_job_details_page(
        site="NoFluffJobs",
        url_hash=job_url.url_hash,
        data=data,
        scrape_run_id=job_url.scrape_run.id,
    )
    
    tracking.update_job_url_s3_key(id=job_url_id, s3_key=key)
    
def parse_job_details(job_url_id: int) -> dict:
    job_url = selectors.find_job_url(id=job_url_id)
    
    assert job_url.s3_key is not None and job_url.s3_key != "", f"cannot parse job details without S3 key: {job_url}"
    
    content = storage.get_job_details_page(job_url.s3_key)
    data = json.loads(content)
    
    salary_data: dict = _parse_salary_data(data=data)
    
    return {
        "external_id": data.get("id"),
        "url": job_url.url,
        "title": data.get("title"),
        "daily_tasks": data.get("specs", {}).get("dailyTasks"),
        "category": data.get("basics", {}).get("category"),
        "seniority": data.get("basics", {}).get("seniority"),
        "technology": data.get("basics", {}).get("technology"),
        "company_url": data.get("company", {}).get("url"),
        "company_name": data.get("company", {}).get("name"),
        "description": data.get("details", {}).get("description"),
        "benefits": data.get("benefits", {}).get("benefits"),
        "salary_range_bottom": salary_data["bottom"],
        "salary_range_top": salary_data["top"],
        "salary_period": salary_data["period"],
        "salary_currency": salary_data["currency"],
        "required_skills": [item.get("value") for item in data.get("requirements", {}).get("musts", {})],
        "nice_to_have_skills": [item.get("value") for item in data.get("requirements", {}).get("nices", {})],
        "requirements": data.get("requirements", {}).get("description"),
        "posted_at": datetime.fromtimestamp(data.get("posted") / 1000),
        "expired_at": data.get("expiresAt"),
        "regions": data.get("regions"),
    }
    
def _parse_salary_data(data: dict):
    results = {
        "bottom": None,
        "top": None,
        "currency": None,
        "period": None,
    }
    
    essentials = data.get("essentials")
    if essentials is None:
        return results
    
    salary = essentials.get("originalSalary")
    if salary is None:
        return results
    
    types = salary.get("types")
    if types is None:
        return results
    
    b2b = types.get("b2b")
    if b2b is None:
        return results
    
    range = b2b.get("range")
    if range is None:
        return results
    
    return {
        "bottom": range[0],
        "top": range[1],
        "period": b2b.get("period"),
        "currency": salary.get("currency")
    }
    
def parse_job_urls(listing_page_data: dict) -> list[str]:
    assert "postings" in listing_page_data, f"'postings' key missing from NoFluffJob data: {listing_page_data}"
    
    job_urls = []
    for posting_data in listing_page_data["postings"]:
        job_urls.append(posting_data["url"])
        
    return job_urls

def find_same_job_urls(
    target_job_url: str, 
    all_job_urls: list[str],
    already_grouped_urls: set[str]
) -> list[str] | None:
    """
    NoFluffJobs create a URL for each region that the job is available in
    For example:
        - data-platform-engineer-kafka-streaming-square-one-resources-remote
        - data-platform-engineer-kafka-streaming-square-one-resources-warszawa
        - data-platform-engineer-kafka-streaming-square-one-resources-lower-silesian
        - data-platform-engineer-kafka-streaming-square-one-resources-kuyavian-pomeranian
        ...
        
    These are all the same job but from the search API it is returned 17 times for 17 different location
    
    This function groups similar URLs together
    """
    if target_job_url in already_grouped_urls:
        return None
    
    same_job_urls = []
    for job_url in all_job_urls:
        if job_url in already_grouped_urls:
            continue
        
        ratio = Levenshtein.ratio(target_job_url, job_url)

        # the string itself
        if ratio == 1.0:
            continue
        
        if ratio > 0.8:
            same_job_urls.append(job_url)
            
    return same_job_urls

def get_root_job_url(
    target_job_url: str, 
    similar_job_urls: list[str],
) -> str | None:
    """
    NoFluffJobs create a URL for each region that the job is available in
    For example:
        - data-platform-engineer-kafka-streaming-square-one-resources-remote
        - data-platform-engineer-kafka-streaming-square-one-resources-warszawa
        - data-platform-engineer-kafka-streaming-square-one-resources-lower-silesian
        - data-platform-engineer-kafka-streaming-square-one-resources-kuyavian-pomeranian
        ...
        
    These are all the same job but from the search API it is returned 17 times for 17 different location
    
    The root URL also gives every information for a job:
        - data-platform-engineer-kafka-streaming-square-one-resources
        
    This function removes the 17 duplicated URLs and return the root one.
    """
    
    results = []
    parts = target_job_url.split("-")
    root_url = ""
    
    for i, part in enumerate(parts):
        root_url += f"{part}-"
        job_count = 0
        
        for job_url in similar_job_urls:
            if job_url.startswith(root_url):
                job_count += 1
            
        results.append({
            "job_count": job_count,
            "part_count": i+1,
            "root_url": root_url,
        })
        
    sorted_results = sorted(results, key=lambda r: r["part_count"], reverse=True)
    best_result = sorted_results[0]
    for r in sorted_results:
        if r["job_count"] > best_result["job_count"]:
            return r["root_url"].strip("-")

    return best_result["root_url"].strip("-")     