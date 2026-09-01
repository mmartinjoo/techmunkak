import chromadb
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from techmunkak.core.config import settings
from techmunkak.embeddings.services import embedder

chroma_client = chromadb.HttpClient(
    host=settings.chroma_host,
    port=settings.chroma_port,
    ssl=settings.chroma_ssl,
)

job_store = Chroma(
    client=chroma_client,
    collection_name="jobs",
    embedding_function=embedder.EMBEDDER,
)

def store_job(content: str, metadata: dict) -> list[str]:
    documents = _chunk(content=content, metadata=metadata)
    return job_store.add_documents(documents)

def query_jobs_by_text(q: str, k: int) -> set[str]:
    results = job_store.similarity_search_with_score(query=q, k=k)
    return set([r[0].metadata["job_key"] for r in results])
        
def query_jobs_by_embedding(embedding: list[float], k: int) -> set[str]:
    results = job_store.similarity_search_by_vector_with_relevance_scores(embedding=embedding, k=k)
    return set([r[0].metadata["job_key"] for r in results])

def _chunk(content: str, metadata: dict) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    
    docs = [
        Document(page_content=content, metadata=metadata)
    ]
    
    return text_splitter.split_documents(docs)