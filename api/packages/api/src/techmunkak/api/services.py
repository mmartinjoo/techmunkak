import json
from techmunkak.core import storage, string
from techmunkak.core.db import pool
from datetime import datetime

def upload_cv_to_s3(filename: str, contents: bytes) -> str:
    return storage.put_pdf(filename=filename, data=contents)

def create_cv_matching_result(cv_s3_key: str, job_keys: list[str]):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.cv_matching_results(cv_s3_key, job_keys)
            values(%s, %s)             
        """, (cv_s3_key, json.dumps(job_keys),))
        
        conn.commit()
        
def get_name_for_uploaded_cv(filename: str) -> str:
    if filename == "" or filename is None:
        raise ValueError(f"missing filename")
        
    parts = filename.split(".")
    base_name = "temp" if len(parts) != 2 else parts[0]
    return f"{string.slug(base_name)}_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf"
    
    