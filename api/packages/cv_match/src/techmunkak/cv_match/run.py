from techmunkak.cv_match import services

def test():
    job_keys = services.match("CVs/Martin Joo.pdf")
    print(job_keys)