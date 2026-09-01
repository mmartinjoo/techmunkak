from techmunkak.cv_match.services.cv_matcher import get_cv_matcher

def test():
    embedding_matcher = get_cv_matcher("embedding")
    embedding_job_keys = embedding_matcher.match(cv_s3_key="CVs/Martin Joo.pdf")
    
    nlp_matcher = get_cv_matcher("nlp")
    nlp_job_keys = nlp_matcher.match(cv_s3_key="CVs/Martin Joo.pdf")
    
    print(embedding_job_keys.union(nlp_job_keys))