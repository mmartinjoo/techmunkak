from techmunkak.cv_match.services.cv_matcher import get_cv_matcher

def test():
    cv_matcher = get_cv_matcher("embedding")
    print(cv_matcher.match(cv_s3_key="CVs/Martin Joo.pdf"))