import json

from techmunkak.core.db import pool


def create_embedded_job(job_key: str, chroma_ids: list[str]):
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.embedded_jobs(job_key, chroma_ids)
            values(%s, %s)             
        """, (job_key, json.dumps(chroma_ids),))
        
        conn.commit()