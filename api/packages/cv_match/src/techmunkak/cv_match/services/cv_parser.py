import io
from pypdf import PdfReader
from techmunkak.core import storage

def parse(cv_s3_key: str) -> str:
    content = storage.get_pdf(cv_s3_key)
    buf = io.BytesIO(content)
    reader = PdfReader(buf)
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        replaced = text.replace("\n", "")
        texts.append(replaced)
        
    return "".join(texts)