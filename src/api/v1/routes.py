"""API routes for version 1.

This module contains the FastAPI routes for the v1 API endpoints,
including semantic search functionality for news articles.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from src.api.v1.dependencies import get_pinecone_db
from src.db.pinecone import PineconeDB
from src.schemas.news_articles import NewsArticleResponse

router = APIRouter()


@router.get("/search", response_model=NewsArticleResponse, summary="Semantic Search")
async def search(
    query: str = Query(..., description="The search query text"),
    top_k: int = Query(3, description="Number of results to return", ge=1, le=10),
    db: PineconeDB = Depends(get_pinecone_db),
) -> NewsArticleResponse:
    """Perform semantic search on news articles.

    Parameters:
        query (str): The search query text to match against articles
        top_k (int): Number of results to return (default: 3, max: 10)
        db (PineconeDB): The PineconeDB instance provided via dependency injection

    Returns:
        List[Dict[str, Any]]: A list of article dictionaries matching the query, sorted by relevance

    Raises:
        HTTPException: If an error occurs during the search process
    """
    try:
        logger.info(f"Executing semantic search with query: '{query}' and top_k: {top_k}")
        results = db.query(text=query, top_k=top_k)

        # Extract the metadata from the search results
        articles = []

        # Handle different result formats (dict vs object)
        if hasattr(results, "matches"):
            matches = results.matches
        elif isinstance(results, dict) and "matches" in results:
            matches = results["matches"]
        else:
            logger.warning(f"Unexpected result format: {type(results)}")
            return NewsArticleResponse(articles=articles, errors=["Unexpected result format"])

        for match in matches:
            # Handle different match formats
            if hasattr(match, "metadata"):
                metadata = match.metadata
                score = getattr(match, "score", 0.0)
            elif isinstance(match, dict):
                metadata = match.get("metadata", {})
                score = match.get("score", 0.0)
            else:
                logger.warning(f"Unexpected match format: {type(match)}")
                continue

            # Add score to the metadata if not present
            if "score" not in metadata:
                metadata["score"] = score

            articles.append(metadata)

        logger.info(f"Found {len(articles)} matching articles")

        return NewsArticleResponse(articles=articles, errors=[])

    except Exception as e:
        logger.error(f"Error during search: {str(e)}")

        raise HTTPException(status_code=500, detail=f"An error occurred during search: {str(e)}") from e
