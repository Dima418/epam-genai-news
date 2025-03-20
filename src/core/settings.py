"""Configuration settings for the application.

This module contains all configuration settings for the application,
including API keys, browser configurations, database settings, and more.
"""
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class APIKeys(BaseSettings):
    """API keys configuration.
    
    Contains API keys required for external services.
    """
    GROQ_API_KEY: str
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str

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
        "The `topics` should be a list of 1-3 items and consist of 1-2 words, where 1 word is more preferable.\n\n"
        "You must only cover the main part of the article, and not include any additional information or opinions "
        "or any `relevant` articles that can be present alongside the article page. "
        "Do not go deeper than the main article content."
    )


class BaseConfig(BaseSettings):
    """Base application configuration.
    
    Contains core application settings like debug mode, host, and port.
    """
    DEBUG: bool = True

    HOST: str = "localhost"
    PORT: int = 8000


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
