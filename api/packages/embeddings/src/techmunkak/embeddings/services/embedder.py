from langchain_mistralai import MistralAIEmbeddings
from techmunkak.core.config import settings

EMBEDDER = MistralAIEmbeddings(
    model=settings.embedder_llm_model,
    api_key=settings.mistral_api_key,
)

def embed(content: str) -> list[float]:
    embeddings = EMBEDDER.embed_documents([content])
    if len(embeddings) != 1:
        raise RuntimeError(f"embedder returned invalid vector: {embeddings}")
    
    return embeddings[0]
