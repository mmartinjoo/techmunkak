from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk(content: str, metadata: dict) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    
    docs = [
        Document(page_content=content, metadata=metadata)
    ]
    
    return text_splitter.split_documents(docs)