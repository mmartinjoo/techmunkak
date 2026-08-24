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

def put_listing_pages(site: str, search_term: str, pages: list[dict], run_id: int) -> list[str]:
    keys = []
    for i, data in enumerate(pages):
        key = f"{site}/{run_id}/{search_term}/{i+1}.json"
        s3.put_object(
            Bucket=settings.s3_bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        keys.append(key)
        
    return keys
    
