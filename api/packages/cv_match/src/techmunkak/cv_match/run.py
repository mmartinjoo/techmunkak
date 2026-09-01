from techmunkak.cv_match.services import parse_cv, extract_skills_from_cv

def test():
    cv_s3_key = "CVs/Martin Joo.pdf"
    text = parse_cv(cv_s3_key=cv_s3_key)
    skills = extract_skills_from_cv(cv_content=text)
    print(skills)