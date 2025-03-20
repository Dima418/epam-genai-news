# GenAI News API

This project implements a News Processing and Search API with semantic search capabilities powered by GenAI and vector databases.

## Features

- News article scraping and processing
- GenAI-powered summarization and topic extraction
- Vector-based semantic search using Pinecone
- RESTful API for searching news articles

## Project Structure

```
.
├── src/
│   ├── api/                  # API endpoints
│   │   └── v1/               # API version 1
│   ├── core/                 # Core settings and configuration
│   ├── data_providers/       # Data sources and scraping
│   ├── db/                   # Database integration
│   ├── embedding/            # Vector embedding handling
│   └── schemas/              # Data models
├── downloaded_files/         # Storage for downloaded data
├── run_fastapi.py            # FastAPI application entry point
├── prepare_db.py             # Database preparation script
└── requirements.txt          # Project dependencies
```

## Setup

### Local Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env` file (see `.env.sample` for reference)

3. Run the database preparation script (to populate the vector database):
   ```
   python prepare_db.py
   ```

4. Start the API server:
   ```
   python run_fastapi.py
   ```

### Docker Setup

1. Make sure Docker and Docker Compose are installed on your system

2. Set up environment variables in `.env` file (see `.env.sample` for reference)

3. Build and start the services:
   
   To run just the API (assuming database is already prepared):
   ```
   docker-compose up api
   ```
   
   To prepare the database:
   ```
   docker-compose up prepare_db
   ```

   To run both (prepare database first, then start API):
   ```
   docker-compose up prepare_db && docker-compose up api
   ```

   Alternatively, you can run the container directly with:
   ```
   # Build the container
   docker build -t genai-news .
   
   # Prepare the database
   docker run --env-file .env genai-news prepare_db
   
   # Run the API
   docker run --env-file .env -p 8000:8000 genai-news run_fastapi
   
   # Run both sequentially
   docker run --env-file .env -p 8000:8000 genai-news both
   ```

## API Endpoints

### Semantic Search

```
GET /api/v1/search?query={search_text}&top_k={num_results}
```

Parameters:
- `query` (required): The search query text
- `top_k` (optional, default=3): Number of results to return

Response:
A JSON array of news articles matching the search query, with each article containing:
- `title`: Article title
- `content`: Article content
- `author`: Article author
- `published_at`: Publication date/time
- `summary`: Article summary
- `topics`: List of topics
- `url`: Article URL
- `score`: Relevance score

## Technologies Used

- FastAPI - Web framework
- Pinecone - Vector database
- Selenium - Web scraping
- Crawl4AI - Extracting and summarizing news articles from web pages
- Loguru - Logging

## License

[License information] 