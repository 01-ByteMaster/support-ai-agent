from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings
from app.exceptions import EmbeddingError
@lru_cache(maxsize=1)
def get_embedder():
    try:return HuggingFaceEmbeddings(model_name=settings.embedding_model,model_kwargs={"device":"cpu"},encode_kwargs={"normalize_embeddings":True})
    except Exception as e:raise EmbeddingError("Embedding model initialization failed") from e
def _valid(v):
    return len(v)==settings.embedding_dimensions and all(isinstance(x,(float,int)) and x==x and abs(x)!=float("inf") for x in v)
def embed_texts(texts):
    try:
        vectors=get_embedder().embed_documents(texts)
        if any(not _valid(v) for v in vectors):raise EmbeddingError("Invalid embedding vector/dimension")
        return vectors
    except EmbeddingError:raise
    except Exception as e:raise EmbeddingError("Embedding generation failed") from e
def embed_query(text):
    try:
        v=get_embedder().embed_query(text)
        if not _valid(v):raise EmbeddingError("Invalid query embedding")
        return v
    except EmbeddingError:raise
    except Exception as e:raise EmbeddingError("Query embedding failed") from e
