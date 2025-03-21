"""Database preparation module.

This module provides functionality to fill the database with news articles
fetched from web sources using web crawlers.
"""
import asyncio
import os
import uuid

from loguru import logger

from src.db.pinecone import PineconeDB
from src.core.settings import settings, BASE_DIR

# NOTE: can requre running the following command to install the required dependencies:
#   > playwright install


DATA_PROVIDER = "web"  # "web" or "file"


def yield_from_file():
    from src.data_providers.data_provider import DataProvider
    from src.data_providers.file.parser import FileParser
    from src.data_providers.file.reader import FileReader
    from src.data_providers.file.decoder import JSONDecoder

    fr = FileReader(file_path=os.path.join(BASE_DIR, "examples", "test-news.txt"))
    parser = FileParser(file_reader=fr, decoder=JSONDecoder())

    for item in DataProvider(parser).provide_data():
        yield item


async def yield_from_web():
    from src.data_providers.data_provider import AsyncDataProvider
    from src.data_providers.web.web_crawler import CrawlingHelper
    from src.data_providers.web.website_scrappers.axios import AxiosScraper

    parser = CrawlingHelper(scrapper=AxiosScraper())

    await parser.start()
    try:
        async for item in AsyncDataProvider(parser).provide_data():
            yield item
    finally:
        await parser.close()


async def fill_db_web():
    """Fill the database with news articles.
    
    Crawls news articles from Axios website, processes them,
    generates embeddings, and stores them in Pinecone database.
    """
    article_property_to_embed = "content"

    db = PineconeDB(index_name="news-articles", namespace=article_property_to_embed)

    embeddings_chunk = []
    chunk_size = 10

    fails_in_a_row = 0
    max_fails_in_a_row = 3

    async for article_data in yield_from_web():

        logger.debug(f"Article data: {article_data}")

        if not article_data:
            fails_in_a_row += 1

            if fails_in_a_row >= max_fails_in_a_row:
                logger.warning(f"Failed to crawl article: {article_data}. Skipping the rest.")
                break

            logger.warning(f"Failed to crawl article: {article_data}.")
            continue

        fails_in_a_row = 0

        article_embedding = db.get_embeddings(article_data[article_property_to_embed])
        upsert_data = {
            "id": str(uuid.uuid4()),
            "values": article_embedding[0].values,
            "metadata": article_data,
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


def fill_db_file():
    article_property_to_embed = "content"

    db = PineconeDB(index_name="news-articles", namespace=article_property_to_embed)

    fails_in_a_row = 0
    max_fails_in_a_row = 3

    for article_data in yield_from_file():
        logger.debug(f"Article data: {article_data}")

        if not article_data:
            fails_in_a_row += 1

            if fails_in_a_row >= max_fails_in_a_row:
                logger.warning(f"Failed to crawl article: {article_data}. Skipping the rest.")
                break

            logger.warning(f"Failed to crawl article: {article_data}.")
            continue

        article_embedding = db.get_embeddings(article_data[article_property_to_embed])
        upsert_data = {
            "id": str(uuid.uuid4()),
            "values": article_embedding[0].values,
            "metadata": article_data,
        }

        db.upsert([upsert_data])


if __name__ == "__main__":
    if DATA_PROVIDER == "web":
        asyncio.run(fill_db_web())
    else:
        fill_db_file()
