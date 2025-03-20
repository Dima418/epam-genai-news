"""News article schemas module.

This module defines the data models for news articles.
"""

from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """News article model.

    This model represents a news article with its metadata and content.

    Attributes:
        title (str): The title of the article
        content (str): The full text content of the article
        author (str): The author of the article
        published_at (str): Publication date and time of the article
        summary (str): A concise summary of the article content
        topics (list[str]): List of topics associated with the article
    """

    title: str = Field(description="The title of the article")
    content: str = Field(description="The full text content of the article")
    author: str = Field(description="The author of the article")
    published_at: str = Field(description="Publication date and time of the article")
    summary: str = Field(description="A concise summary of the article content")
    topics: list[str] = Field(description="List of topics associated with the article")

    @staticmethod
    def get_properties_names() -> list[str]:
        """Get the names of all properties in the NewsArticle model.

        Returns:
            list[str]: List of property names
        """
        return ["title", "content", "author", "published_at", "summary", "topics"]


class NewsArticleQueryResult(NewsArticle):
    """News article response model.

    This model extends the NewsArticle model with additional fields for response data.

    Attributes:
        url (str): The URL of the article
        score (str): The relevance score of the article
    """

    url: str = Field(description="The URL of the article")
    score: float = Field(description="The relevance score of the article")


class NewsArticleResponse(BaseModel):
    """News article response model.

    This model represents a list of news articles in the response.

    Attributes:
        articles (list[NewsArticleQueryResult]): List of news articles
    """

    articles: list[NewsArticleQueryResult] = Field(description="List of news articles")
    errors: list[str] = Field(description="List of errors")
