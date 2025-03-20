"""
Tests for the API endpoints.

This module contains tests for the API endpoints using FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from run_fastapi import app


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    return TestClient(app)


def test_search_endpoint(client, monkeypatch):
    """Test the search endpoint."""
    # Mock the PineconeDB query method to avoid actual API calls
    from unittest.mock import MagicMock

    import src.db.pinecone

    # Create a mock for the query result
    mock_query_result = MagicMock()
    mock_query_result.matches = [
        MagicMock(
            id="test-id-1",
            score=0.95,
            metadata={
                "title": "Test Article 1",
                "content": "Test content 1",
                "author": "Test Author 1",
                "published_at": "2023-01-01T12:00:00",
                "summary": "Test summary 1",
                "topics": ["test", "article"],
                "url": "https://example.com/article1",
            },
        ),
        MagicMock(
            id="test-id-2",
            score=0.85,
            metadata={
                "title": "Test Article 2",
                "content": "Test content 2",
                "author": "Test Author 2",
                "published_at": "2023-01-02T12:00:00",
                "summary": "Test summary 2",
                "topics": ["test", "article"],
                "url": "https://example.com/article2",
            },
        ),
    ]

    # Create a mock for the PineconeDB
    mock_db = MagicMock()
    mock_db.query.return_value = mock_query_result

    # Patch the PineconeDB constructor to return our mock
    def mock_pinecone_db(*args, **kwargs):
        return mock_db

    monkeypatch.setattr(src.db.pinecone, "PineconeDB", mock_pinecone_db)

    # Make the request
    response = client.get("/api/v1/search?query=test&top_k=2")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test Article 1"
    assert data[0]["score"] == 0.95
    assert data[1]["title"] == "Test Article 2"

    # Verify the mock was called correctly
    mock_db.query.assert_called_once_with(text="test", top_k=2)


def test_search_endpoint_error(client, monkeypatch):
    """Test the search endpoint with an error."""
    # Mock the PineconeDB query method to raise an exception
    from unittest.mock import MagicMock

    import src.db.pinecone

    # Create a mock for the PineconeDB
    mock_db = MagicMock()
    mock_db.query.side_effect = Exception("Test exception")

    # Patch the PineconeDB constructor to return our mock
    def mock_pinecone_db(*args, **kwargs):
        return mock_db

    monkeypatch.setattr(src.db.pinecone, "PineconeDB", mock_pinecone_db)

    # Make the request
    response = client.get("/api/v1/search?query=test")

    # Assertions
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Test exception" in data["detail"]
