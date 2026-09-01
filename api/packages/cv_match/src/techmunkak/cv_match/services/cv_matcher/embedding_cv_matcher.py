from techmunkak.cv_match.services import cv_parser
from techmunkak.embeddings.services import embedder, vector_store

MATCHER_TYPE = "embedding"

def match(cv_s3_key: str) -> set[str]:
    content = cv_parser.parse(cv_s3_key=cv_s3_key)
    embedding = embedder.embed(content=content)
    job_keys = vector_store.query_jobs_by_embedding(embedding=embedding, k=5)
    return set(job_keys)