"""
Configuration module for RAG system parameters
"""
import os
from typing import Dict, Any

# Similarity threshold configuration
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))

# Chunking configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
BOOK_COLLECTION_NAME = os.getenv("BOOK_COLLECTION_NAME", "book")

# Embedding configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# RAG Chain configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))

# Search configuration
SEARCH_LIMIT = int(os.getenv("SEARCH_LIMIT", "5"))

# Configuration dictionary for easy access
RAG_CONFIG: Dict[str, Any] = {
    "similarity_threshold": SIMILARITY_THRESHOLD,
    "chunk_size": CHUNK_SIZE,
    "chunk_overlap": CHUNK_OVERLAP,
    "qdrant_url": QDRANT_URL,
    "qdrant_api_key": QDRANT_API_KEY,
    "book_collection_name": BOOK_COLLECTION_NAME,
    "embedding_model": EMBEDDING_MODEL,
    "llm_model": LLM_MODEL,
    "llm_temperature": LLM_TEMPERATURE,
    "search_limit": SEARCH_LIMIT
}


def get_config(key: str, default=None):
    """
    Get configuration value by key
    """
    return RAG_CONFIG.get(key, default)


def update_config(key: str, value: Any):
    """
    Update configuration value by key
    """
    RAG_CONFIG[key] = value