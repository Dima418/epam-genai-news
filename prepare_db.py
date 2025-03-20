"""Database preparation module.

This module provides functionality to fill the database with news articles
fetched from web sources using web crawlers.
"""
import asyncio
import uuid

from loguru import logger

from src.data_providers.web.web_crawler import CrawlingHelper
from src.data_providers.web.website_scrappers.axios import AxiosScraper
from src.db.pinecone import PineconeDB
from src.core.settings import settings
from src.schemas.news_articles import NewsArticle

# NOTE: can requre running the following command to install the required dependencies:
#   > playwright install


async def fill_db():
    """Fill the database with news articles.
    
    Crawls news articles from Axios website, processes them,
    generates embeddings, and stores them in Pinecone database.
    """
    article_property_to_embed = "content"

    scrapper = AxiosScraper()
    crawler = CrawlingHelper()
    db = PineconeDB(index_name="news-articles", namespace=article_property_to_embed)

    processed_ids = set()
    embeddings_chunk = []
    chunk_size = 10

    fails_in_a_row = 0
    max_fails_in_a_row = 0

    async with crawler:
        for url in scrapper.articles_urls_generator():
            article_data = await crawler.fetch_and_process_page(
                url=url,
                required_keys=NewsArticle.get_properties_names(),
                session_id="axios_crawl_session",
                processed_ids=processed_ids,
            )

            if not article_data:
                fails_in_a_row += 1

                if fails_in_a_row >= max_fails_in_a_row:
                    logger.warning(f"Failed to crawl article: {url}. Skipping the rest.")
                    break

                logger.warning(f"Failed to crawl article: {url}")
                continue

            fails_in_a_row = 0

            article_embedding = db.get_embeddings(article_data[article_property_to_embed])
            upsert_data = {
                "id": str(uuid.uuid4()),
                "values": article_embedding[0].values,
                "metadata": article_data | {"url": url},
            }
            embeddings_chunk.append(upsert_data)

            if settings.base_config.IS_LIMITED and len(embeddings_chunk) >= settings.base_config.ITEMS_LIMIT:
                logger.warning(f"Limit of {settings.base_config.ITEMS_LIMIT} items reached.")
                embeddings_chunk = embeddings_chunk[: settings.base_config.ITEMS_LIMIT]  # leave only the first N items
                break

            if not settings.base_config.IS_LIMITED and len(embeddings_chunk) >= chunk_size:
                logger.info(f"Upserting {len(embeddings_chunk)} embeddings to Pinecone.")
                db.upsert(embeddings_chunk)
                embeddings_chunk = []

        if embeddings_chunk:
            logger.info(f"{len(embeddings_chunk)} embeddings left. Upserting to Pinecone.")
            db.upsert(embeddings_chunk)


if __name__ == "__main__":
    asyncio.run(fill_db())
