"""
MedIntel AI — Application configuration.
Loads environment variables and provides centralized settings.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # App
    APP_NAME: str = "MedIntel AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chroma_db")
    CHROMA_COLLECTION_NAME: str = "medintel_regulations"

    # Documents
    DOCS_DIR: str = str(BASE_DIR / "data" / "documents")

    # RAG
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    TEMPERATURE: float = 0.2

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
