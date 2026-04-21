from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "rag-service"
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    embedding_model: str = "text-embedding-3-small"
    milvus_mode: str = "lite"
    rag_milvus_uri: str = ".run/milvus/canvas_ai.db"
    milvus_token: Optional[str] = None
    milvus_collection_prefix: str = "canvas_rag_"
    milvus_vector_dim: int = 1536
    milvus_metric_type: str = "COSINE"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
