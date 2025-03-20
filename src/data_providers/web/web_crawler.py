"""Web crawler module for fetching and processing web pages.

This module provides functionality to crawl web pages and extract structured data
using language models.
"""
import json

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, LLMConfig, LLMExtractionStrategy
from loguru import logger

from src.core.settings import settings
from src.schemas.news_articles import NewsArticle


class CrawlingHelper:
    """Helper class for web crawling.
    
    Provides methods to crawl web pages and extract structured data using LLM.
    """
    def __init__(self, browser_config: BrowserConfig | None = None) -> None:
        """Initialize the CrawlingHelper.
        
        Args:
            browser_config (BrowserConfig | None, optional): Browser configuration.
                If None, default configuration will be used. Defaults to None.
        """
        logger.info("Initializing CrawlingHelper...")
        self._browser_config = browser_config or self.get_default_browser_config()
        self._crawler = AsyncWebCrawler(config=self._browser_config)

    @staticmethod
    def get_default_browser_config() -> BrowserConfig:
        """Returns the browser configuration for the crawler.

        Returns:
            BrowserConfig: The configuration settings for the browser.
        """
        # https://docs.crawl4ai.com/core/browser-crawler-config/
        return BrowserConfig(
            browser_type=settings.browser_config.CRAWL4AI_BROWSER,
            headless=settings.browser_config.CRAWL4AI_HEADLESS,
            verbose=False,
        )

    @staticmethod
    def get_default_llm_strategy() -> LLMExtractionStrategy:
        """Returns the configuration for the language model extraction strategy.

        Returns:
            LLMExtractionStrategy: The settings for how to extract data using LLM.
        """
        # https://docs.crawl4ai.com/api/strategies/#llmextractionstrategy
        llm_config = LLMConfig(
            provider=settings.llm_config.LLM_PROVIDER,
            api_token=settings.api_keys.GROQ_API_KEY,
        )
        return LLMExtractionStrategy(
            llm_config=llm_config,
            schema=NewsArticle.model_json_schema(),
            extraction_type="schema",
            instruction=settings.llm_config.LLM_INSTRUCTION,
            input_format="markdown",
            verbose=True,
        )

    @staticmethod
    def contains_all_required_keys(item: dict, required_keys: list) -> bool:
        """Check if a dictionary contains all required keys.
        
        Args:
            item (dict): Dictionary to check
            required_keys (list): List of keys that must be present
            
        Returns:
            bool: True if all required keys are present, False otherwise
        """
        return all(key in item for key in required_keys)

    async def fetch_and_process_page(
        self,
        url: str,
        *,
        session_id: str,
        required_keys: list[str],
        processed_ids: set[str],
        llm_strategy: LLMExtractionStrategy | None = None,
    ) -> dict | None:
        """Fetch and process a web page to extract structured data.
        
        Args:
            url (str): URL to fetch and process
            session_id (str): Session identifier for the crawler
            required_keys (list[str]): List of keys required in the extracted data
            processed_ids (set[str]): Set of already processed URLs
            llm_strategy (LLMExtractionStrategy | None, optional): Strategy for LLM extraction.
                If None, default strategy will be used. Defaults to None.
                
        Returns:
            dict | None: Extracted data if successful, None otherwise
        """
        if not llm_strategy:
            llm_strategy = self.get_default_llm_strategy()

        fetch_result = await self._crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=llm_strategy,
                session_id=session_id,
            ),
        )

        if not (fetch_result.success and fetch_result.extracted_content):
            logger.error(f"Error crawling results from {url}.")
            return None

        extracted_data = json.loads(fetch_result.extracted_content)
        if not extracted_data:
            logger.error(f"No data found on page {url}.")
            return None

        logger.debug("Extracted data:", extracted_data)

        complete_items = []
        for item in extracted_data:
            if error := item.pop("error", None):
                logger.error(f"Error processing item: {error} on page {url}")

            if not self.contains_all_required_keys(item, required_keys):
                continue

            if url in processed_ids:
                return None

            processed_ids.add(url)

            complete_items.append(item)

        if not complete_items:
            logger.error(f"No complete items found on page {url}.")
            return None

        if len(complete_items) > 1:
            logger.warning(f"Multiple items found on page {url}")

        return complete_items[0]

    async def start(self) -> AsyncWebCrawler:
        """Start the web crawler.
        
        Returns:
            AsyncWebCrawler: Started web crawler instance
        """
        return await self._crawler.start()

    async def close(self) -> None:
        """Close the web crawler and release resources."""
        return await self._crawler.close()

    async def __aenter__(self) -> AsyncWebCrawler:
        """Enter the async context manager.
        
        Returns:
            AsyncWebCrawler: Started web crawler instance
        """
        return await self._crawler.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager and cleanup resources."""
        await self._crawler.close()
