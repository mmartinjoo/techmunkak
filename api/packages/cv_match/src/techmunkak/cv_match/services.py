import io
from pypdf import PdfReader
from techmunkak.core import storage
from techmunkak.skill_model.services.inference import inference as skill_model

def parse_cv(cv_s3_key: str) -> str:
    content = storage.get_pdf(cv_s3_key)
    buf = io.BytesIO(content)
    reader = PdfReader(buf)
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        replaced = text.replace("\n", "")
        texts.append(replaced)
        
    return "".join(texts)
    
def extract_skills_from_cv(cv_content: str) -> list[str]:
    skills = skill_model(text=cv_content)
    return skills