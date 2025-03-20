"""Pinecone Vector Database module.

This module provides an interface to interact with Pinecone vector database
for storing and retrieving vector embeddings.
"""

import time
from typing import Any

from loguru import logger
from pinecone import Pinecone, ServerlessSpec
from pinecone.core.openapi.db_data.model.query_response import QueryResponse
from pinecone.data.index import Index
from pinecone.enums import Metric

from src.core.settings import settings
from src.embedding.helpers.pinecone import PineconeEmbeddingHelper


class PineconeDBError(Exception):
    """Exception raised for Pinecone database errors."""

    pass


class PineconeDB:
    """Pinecone Vector Database client.

    This class provides methods to interact with Pinecone for storing,
    retrieving, and querying vector embeddings for news articles.
    """

    def __init__(self, index_name: str, namespace: str | None = "default") -> None:
        """Initialize the Pinecone database client.

        Args:
            index_name (str): Name of the Pinecone index to use
            namespace (str, optional): Namespace within the index. Defaults to "default".
        """
        self._index_name = index_name
        self._namespace = namespace
        self._pc = Pinecone(api_key=settings.api_keys.PINECONE_API_KEY)
        self._embedding_helper = PineconeEmbeddingHelper(self._pc)
        self._pci = self._get_or_create_index()

    def _get_or_create_index(self) -> Index:
        """Get or create a Pinecone index.

        Returns:
            Index: The Pinecone index object

        Raises:
            PineconeDBError: If the index cannot be created
        """
        # Check if index already exists
        for index in self._pc.list_indexes():
            if index.name == self._index_name:
                logger.info(f"Using existing Pinecone index: {self._index_name}")
                return self._pc.Index(self._index_name)

        # Create new index
        logger.info(f"Creating new Pinecone index: {self._index_name}")
        self._pc.create_index(
            name=self._index_name,
            dimension=self._embedding_helper.get_dimension(),
            metric=Metric.COSINE,
            spec=ServerlessSpec(
                cloud=settings.pinecone_config.PINECONE_CLOUD, region=settings.pinecone_config.PINECONE_REGION
            ),
        )
        return self._pc.Index(self._index_name)

    def get_embeddings(self, data_input: str | list[str]) -> list[dict[str, Any]]:
        """Generate embeddings for input text.

        Args:
            data_input (str | list[str]): Text to generate embeddings for

        Returns:
            List of embeddings
        """
        return self._embedding_helper.generate_embedding(data_input)

    def upsert(self, upsert_data: list[dict[str, Any]]):
        """Insert or update vectors in the Pinecone index.

        Args:
            upsert_data (list[dict[str, Any]]): List of vectors to upsert

        Raises:
            PineconeDBError: If the index is not ready or upsert fails
        """
        # Wait for the index to be ready
        for _ in range(10):
            if self._pc.describe_index(self._index_name).status["ready"]:
                break
            time.sleep(1)
        else:
            raise PineconeDBError("Index is not ready after 10 seconds")

        try:
            self._pci.upsert(
                vectors=upsert_data,
                namespace=self._namespace,
            )
            logger.success(f"Successfully upserted {len(upsert_data)} vectors to {self._index_name}")
        except Exception as e:
            logger.exception(f"Failed to upsert data: {e}")
            raise PineconeDBError(f"Failed to upsert data: {str(e)}") from e

    def query(self, text: str, top_k: int = 5) -> QueryResponse:
        """Query the vector database for similar vectors.

        Args:
            text (str): Query text to find similar vectors
            top_k (int, optional): Number of results to return. Defaults to 5.

        Returns:
            Query results from Pinecone
        """
        logger.debug(f"Querying Pinecone index {self._index_name} with: '{text[:50]}...' (top_k={top_k})")
        embedding = self._embedding_helper.generate_embedding(text)
        return self._pci.query(
            vector=embedding[0].values,
            top_k=top_k,
            include_values=False,
            include_metadata=True,
            namespace=self._namespace,
        )

    def delete(self) -> None:
        """Delete the entire Pinecone index."""
        logger.warning(f"Deleting Pinecone index: {self._index_name}")
        self._pc.delete_index(self._index_name)
