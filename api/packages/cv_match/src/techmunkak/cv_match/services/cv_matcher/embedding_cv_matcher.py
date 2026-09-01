from techmunkak.cv_match.services import cv_parser

MATCHER_TYPE = "embedding"

def match(cv_s3_key: str) -> list[str]:
    content = cv_parser.parse(cv_s3_key=cv_s3_key)
    print(content)