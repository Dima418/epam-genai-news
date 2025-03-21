"""Configuration settings for the application.

This module contains all configuration settings for the application,
including API keys, browser configurations, database settings, and more.
"""
import os
from datetime import datetime

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class APIKeys(BaseSettings):
    """API keys configuration.
    
    Contains API keys required for external services.
    """
    GROQ_API_KEY: str | None = None
    PINECONE_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=os.path.join(BASE_DIR, ".env"),
    )


class BrowserConfig(BaseSettings):
    """Browser configuration settings.
    
    Contains settings for browser automation used in web scraping.
    """
    CRAWL4AI_BROWSER: str = "chromium"
    CRAWL4AI_HEADLESS: bool = True
    SELENIUM_BROWSER: str = "chrome"
    SELENIUM_HEADLESS: bool = True


class PineconeConfig(BaseSettings):
    """Pinecone database configuration.
    
    Contains settings for Pinecone vector database.
    """
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"


class LLMConfig(BaseSettings):
    """Language model configuration.
    
    Contains settings for language model providers and instructions.
    """
    LLM_PROVIDER: str = "groq/deepseek-r1-distill-llama-70b"
    LLM_INPUT_FORMAT: str = "markdown"
    LLM_INSTRUCTION: str = (
        "Extract the `title`, `content`, `author`, and `published_at` of the provided news article "
        "and generate a `summary` that captures key points and identifying the main `topics` of of the article.\n\n"
        "The `summary` should be a concise representation of the article's content, "
        "and the `topics` should be a list of key themes or subjects covered in the article. "
        "The `summary` should be no more than 2 sentences long."
        "The `topics` should be a list of up to 3 most relevant topics. "
        "The topic must be described using 1 word only. \n\n"
        "The `content` should be a complete and full representation of the whole article's content. "
        "Do not go deeper than the main article content. \n\n"
        "If the article was published recently and you can't find the exact `published_at` date value, there can be "
        "a message like 'Published `N` hour[s] ago' or 'Published `N` day[s] ago'. "
        "In this case, you can use the current date and time as the `published_at` value. "
        f"For the reference, today\'s date is {datetime.now().isoformat()} (ISO format). \n\n"
        "The `author` field should contain the full name of the author of the article. "
        "If unable to find the author's name, try to look for the author's name in the article's metadata or " 
        "somewhere near the publishing date. The author of the article must be always present. \n\n"
        "All fields are mandatory. If any of the fields are missing, the extraction should be considered as failed."
    )


class BaseConfig(BaseSettings):
    """Base application configuration.
    
    Contains core application settings like debug mode, host, and port.
    """
    DEBUG: bool = True

    HOST: str = "localhost"
    PORT: int = 8000

    IS_LIMITED: bool = True
    ITEMS_LIMIT: int = 5


class Settings(BaseSettings):
    """Main settings container.
    
    Aggregates all configuration settings into a single container.
    """
    api_keys: APIKeys = APIKeys()
    browser_config: BrowserConfig = BrowserConfig()
    pinecone_config: PineconeConfig = PineconeConfig()
    llm_config: LLMConfig = LLMConfig()
    base_config: BaseConfig = BaseConfig()


settings = Settings()
