import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Clinical Knowledge Graph & Intelligent Document Assistant"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./clinical_kg.db"
    )

    # Retrieval & Graph Config
    top_k_chunks: int = 4
    similarity_threshold: float = 0.20
    max_graph_hops: int = 2

    # LLM Settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "tfidf")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
