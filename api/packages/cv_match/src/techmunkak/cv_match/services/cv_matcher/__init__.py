from typing import Protocol, TypeAlias
from techmunkak.cv_match.services.cv_matcher import nlp_cv_matcher

JobKeys: TypeAlias = list[str]

class CvMatcher(Protocol):
    def match(cv_s3_key: str) -> JobKeys: ...
    
CV_MATCHERS: dict[str, CvMatcher] = {
    nlp_cv_matcher.MATCHER_TYPE: nlp_cv_matcher,
}

def get_cv_matcher(matcher_type: str) -> CvMatcher:
    try:
        return CV_MATCHERS[matcher_type]
    except KeyError:
        raise ValueError(f"unknown cv matcher type: {matcher_type}")