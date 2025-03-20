"""WebDriver module for browser automation.

This module provides functionality to create and configure WebDriver instances
for browser automation and web scraping.
"""
from selenium import webdriver
from seleniumbase import Driver

from src.core.settings import settings


def get_driver(headless: bool) -> webdriver.Chrome:
    """Create and configure a WebDriver instance.
    
    Args:
        headless (bool): Whether to run the browser in headless mode
        
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    return Driver(
        browser=settings.browser_config.SELENIUM_BROWSER,
        headless=headless,
        multi_proxy=True,
        undetectable=True,
        log_cdp_events=True,
        no_sandbox=True,
        disable_gpu=True,
        page_load_strategy="eager",
    )
