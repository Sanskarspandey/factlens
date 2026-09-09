"""Core configuration and settings for FactLens."""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings and configuration."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Info
    PROJECT_NAME: str = "FactLens"
    VERSION: str = "0.3.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Storage Paths
    DATABASE_URL: str = "sqlite:///./data/factlens.db"
    UPLOAD_DIR: str = "./data/uploads"
    VECTOR_STORE_DIR: str = "./data/vector_store"

    # Configurable LLM Provider
    # Supported: "mock", "gemini", "openai"
    LLM_PROVIDER: str = Field(default="gemini", description="Options: gemini, openai, mock")
    LLM_MODEL: str = "gemini-1.5-pro"
    LLM_API_KEY: Optional[str] = None
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 4096

    # Embedding & Vector Database
    EMBEDDING_PROVIDER: str = "sentence-transformers"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_DB_TYPE: str = "chroma"

    # Grounding & Extraction Rules
    MAX_FACTS_PER_PAGE: int = 15
    ENABLE_BOUNDING_BOX_EXTRACTION: bool = True
    CANDIDATE_TOP_K: int = 10
    CANDIDATE_MIN_SCORE: float = 0.30

    # Phase 3 Reconciliation Rules & Numeric Tolerances
    MATCH_TOLERANCE: float = 0.01  # 1% relative tolerance for exact numeric agreement
    POSSIBLE_MATCH_TOLERANCE: float = 0.05  # 5% relative tolerance for close agreement


settings = Settings()
