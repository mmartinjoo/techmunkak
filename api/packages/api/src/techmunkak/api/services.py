import json
from techmunkak.core import storage
from techmunkak.core.db import pool

def upload_cv_to_s3(filename: str, contents: bytes) -> str:
    return storage.put_pdf(filename=filename, data=contents)

def create_cv_matching_result(cv_s3_key: str, job_keys: list[str]):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.cv_matching_results(cv_s3_key, job_keys)
            values(%s, %s)             
        """, (cv_s3_key, json.dumps(job_keys),))
        
        conn.commit()