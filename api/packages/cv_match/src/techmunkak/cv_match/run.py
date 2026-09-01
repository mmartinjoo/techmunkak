from techmunkak.cv_match.services.cv_matcher import get_cv_matcher

def match_cv(cv_s3_key: str) -> list[str]:
    embedding_matcher = get_cv_matcher("embedding")
    embedding_job_keys = embedding_matcher.match(cv_s3_key=cv_s3_key)
    
    nlp_matcher = get_cv_matcher("nlp")
    nlp_job_keys = nlp_matcher.match(cv_s3_key=cv_s3_key)
    
    return embedding_job_keys.union(nlp_job_keys)