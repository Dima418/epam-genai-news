"""Axios website scraper module.

This module provides functionality to scrape news articles from Axios website.
"""
import time

from loguru import logger
from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase.undetected import WebElement

from src.core.settings import settings
from src.data_providers.web.driver import get_driver


class AxiosSelectorsXpath:
    """XPath selectors for Axios website elements."""
    ARTICLE_LINKS = "//article//header//a"
    VIEW_MORE_BUTTON = "//span[contains(text(), 'View more stories')]"


class AxiosScraper:
    """Scraper for Axios news website."""
    MAIN_URL = "https://www.axios.com/"

    def __init__(self, headless: bool = settings.browser_config.SELENIUM_HEADLESS) -> None:
        """Initialize the AxiosScraper.
        
        Args:
            headless (bool, optional): Whether to run the browser in headless mode.
                Defaults to settings.browser_config.SELENIUM_HEADLESS.
        """
        logger.info("Initializing AxiosScraper...")
        self._headless = headless
        self._driver = get_driver(headless)

    def _slow_scroll_down(self, *, current_height: int, max_height: int, scroll_step: int = 800) -> int:
        # Scroll down in smaller increments
        while current_height < max_height:
            self._driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            time.sleep(0.5)  # Short pause between each scroll step to allow content to load
            current_height = self._driver.execute_script("return window.scrollY + window.innerHeight")
        return current_height

    def _get_load_button(self, xpath: str, timeout: int = 3) -> WebElement | None:
        try:
            return WebDriverWait(self._driver, timeout).until(
                expected_conditions.element_to_be_clickable((By.XPATH, xpath))
            )
        except TimeoutException:
            return None

    def _get_new_links(self, existing_collection: set[str]) -> set[str]:
        new_links = set()

        try:
            article_links = self._driver.find_elements(By.XPATH, AxiosSelectorsXpath.ARTICLE_LINKS)
        except StaleElementReferenceException:
            logger.info("Stale element reference, retrying...")
            return new_links

        for link in article_links:
            href = link.get_attribute("href")

            if href not in existing_collection:
                new_links.add(href)

                existing_collection.add(href)

        return new_links

    def articles_urls_generator(self) -> str:
        """Generate URLs of Axios news articles.
        
        This generator function crawls the Axios website, scrolls down to load more content,
        and yields URLs of news articles as they are discovered.
        
        Yields:
            str: URL of a news article
        """
        self._driver.get(self.MAIN_URL)

        article_urls = set()
        max_height = self._driver.execute_script("return document.body.scrollHeight")
        current_height = 0

        try:
            while True:
                current_height = self._slow_scroll_down(current_height=current_height, max_height=max_height)

                # Collect article links
                new_links = self._get_new_links(article_urls)
                logger.debug(f"Collected {len(new_links)} new article links.")

                yield from new_links

                # Check for the "View more stories" button
                view_more_button = self._get_load_button(xpath=AxiosSelectorsXpath.VIEW_MORE_BUTTON)

                if view_more_button is None:
                    logger.info("No more content to load. Exiting.")
                    break

                # Click the button
                view_more_button.click()
                time.sleep(2)

                # Update the new height after clicking the button
                max_height = self._driver.execute_script("return document.body.scrollHeight")
        finally:
            self._driver.quit()
