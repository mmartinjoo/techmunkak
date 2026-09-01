import io
from techmunkak.core import storage

def upload_cv_to_s3(filename: str, contents: bytes) -> str:
    return storage.put_pdf(filename=filename, data=contents)