from techmunkak.core.config import settings
import boto3
import json

s3 = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
)

try:
    s3.head_bucket(Bucket=settings.s3_bucket)
except Exception:
    s3.create_bucket(Bucket=settings.s3_bucket)

def put_listing_page(site: str, search_term: str, data: dict, page: int, scrape_run_id: int) -> str:
    key = f"{site}/{scrape_run_id}/search_terms/{search_term}/{page}.json"
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json"
    )
        
    return key
    
def put_job_details_page(site: str, url_hash: str, data: dict, scrape_run_id: int) -> str:
    key = f"{site}/{scrape_run_id}/jobs/{url_hash}.json"
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json"
    )
        
    return key

def get_job_details_page(key: str) -> str:
    resp = s3.get_object(
        Bucket=settings.s3_bucket,
        Key=key,
    )
    
    return resp["Body"].read().decode("utf-8")