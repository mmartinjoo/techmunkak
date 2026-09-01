from techmunkak.cv_match import services

def test():
    cv_s3_key = "CVs/Martin Joo.pdf"
    text = services.parse_cv(cv_s3_key=cv_s3_key)
    skills = services.extract_skills_from_cv(cv_content=text)
    services.find_matching_jobs(skills)
    