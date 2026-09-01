import chromadb
from langchain_mistralai import MistralAIEmbeddings
from langchain_chroma import Chroma
from techmunkak.core.config import settings
from techmunkak.embeddings.services import chunker

embedder = MistralAIEmbeddings(
    model="mistral-embed",
    api_key=settings.mistral_api_key,
)

chroma_client = chromadb.HttpClient(
    host=settings.chroma_host,
    port=settings.chroma_port,
    ssl=settings.chroma_ssl,
)

job_store = Chroma(
    client=chroma_client,
    collection_name="jobs",
    embedding_function=embedder,
)

def store_job(content: str, metadata: dict) -> list[str]:
    documents = chunker.chunk(content=content, metadata=metadata)
    return job_store.add_documents(documents)

def query_jobs(q: str, k: int):
    results = job_store.similarity_search_with_score(query=q, k=k)
    print(f"query: {q}")
    for i, (doc, score) in enumerate(results, 1):
        print(f"result {i}")
        print(f"content: {doc.page_content[:150]}...")
        print(f"metadata: {doc.metadata}...")
        print(f"similarity: {1-score}")