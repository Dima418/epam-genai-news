"""API dependencies for FastAPI.

This module contains dependency functions for FastAPI routes,
allowing for efficient reuse of resources such as database connections.
"""
from fastapi import Depends
from functools import lru_cache

from src.db.pinecone import PineconeDB


@lru_cache(maxsize=1)
def get_pinecone_db_singleton(
    index_name: str = "news-articles", 
    namespace: str = "content"
) -> PineconeDB:
    """Creates a singleton instance of PineconeDB.
    
    This function uses lru_cache to ensure only one instance is created
    for the entire application lifecycle.
    
    Args:
        index_name: Name of the Pinecone index to use
        namespace: Namespace within the index
        
    Returns:
        PineconeDB: The singleton PineconeDB instance
    """
    return PineconeDB(index_name=index_name, namespace=namespace)


def get_pinecone_db() -> PineconeDB:
    """Provides the PineconeDB instance as a FastAPI dependency.
    
    This dependency ensures the same PineconeDB instance is reused
    across all requests.
    
    Returns:
        PineconeDB: The singleton PineconeDB instance
    """
    return get_pinecone_db_singleton() 