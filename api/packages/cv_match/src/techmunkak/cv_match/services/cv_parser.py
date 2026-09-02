import io
from pypdf import PdfReader
from techmunkak.core import storage

def parse(cv_s3_key: str) -> str:
    content = storage.get_pdf(cv_s3_key)
    if content == "" or content is None:
        raise ValueError("CV content is empty")
        
    buf = io.BytesIO(content)
    reader = PdfReader(buf)
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        replaced = text.replace("\n", "")
        texts.append(replaced)
        
    content = "".join(texts)
    
    if content == "":
        raise ValueError("CV content is empty")
    
    return content