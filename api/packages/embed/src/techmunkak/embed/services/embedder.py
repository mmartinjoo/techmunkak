from langchain_mistralai import MistralAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from techmunkak.core.config import settings
import chromadb
from techmunkak.embed.models import EmbeddableJob

embedder = MistralAIEmbeddings(
    model="mistral-embed",
    api_key=settings.mistral_api_key,
)

chroma_client = chromadb.HttpClient(
    host=settings.chroma_host,
    port=settings.chroma_port,
    ssl=settings.chroma_ssl,
)

vector_store = Chroma(
    client=chroma_client,
    collection_name="jobs",
    embedding_function=embedder,
)

def embed(job: EmbeddableJob):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    
    docs = [
        Document(page_content=job.content, metadata={"job_key": job.job_key})
    ]
    
    chunks = text_splitter.split_documents(docs)
    return vector_store.add_documents(chunks)
    
def query(q: str, k: int):
    results = vector_store.similarity_search_with_score(query=q, k=k)
    print(f"query: {q}")
    for i, (doc, score) in enumerate(results, 1):
        print(f"result {i}")
        print(f"content: {doc.page_content[:150]}...")
        print(f"metadata: {doc.metadata}...")
        print(f"similarity: {1-score}")