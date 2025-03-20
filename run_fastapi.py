"""FastAPI application entry point for the GenAI News API.

This module initializes the FastAPI application, sets up middlewares,
and registers API routes.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import router as api_v1_router
from src.core.settings import settings

# Create FastAPI application
app = FastAPI(
    title="GenAI News API",
    description="API for news scraping, processing, and semantic search",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include router with prefix
app.include_router(api_v1_router, prefix="/api/v1")


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "run_fastapi:app",
        host=settings.base_config.HOST,
        port=settings.base_config.PORT,
        reload=settings.base_config.DEBUG,
    )
