from techmunkak.cv_match.services.cv_matcher import get_cv_matcher

def test():
    cv_matcher = get_cv_matcher("nlp")
    print(cv_matcher.match(cv_s3_key="CVs/Martin Joo.pdf"))