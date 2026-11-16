
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "development"
    log_level: str = "INFO"

    # Database
    database_url: str

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dimensions: int = 384

    # Chunking
    chunk_size: int = Field(default=900, gt=0)
    chunk_overlap: int = Field(default=120, ge=0)

    # Retrieval
    rag_top_k: int = Field(default=5, gt=0)
    rag_min_similarity: float = Field(default=0.45, ge=0, le=1)
    rag_max_context_chunks: int = Field(default=5, gt=0)

    # Gemini
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    # Security
    admin_api_token: str = "change-me"

    # Knowledge base
    knowledge_base_path: str = "data/knowledge_base"


settings = Settings()
