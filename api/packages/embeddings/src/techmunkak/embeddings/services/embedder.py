from langchain_mistralai import MistralAIEmbeddings
from langchain_core.documents import Document
from techmunkak.core.config import settings

embedder = MistralAIEmbeddings(
    model="mistral-embed",
    api_key=settings.mistral_api_key,
)

def embed(content: str) -> list[float]:
    embeddings = embedder.embed_documents([content])
    if len(embeddings) != 1:
        raise RuntimeError(f"embedder returned invalid vector: {embeddings}")
    
    return embeddings[0]
