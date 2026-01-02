# Quickstart: Docusaurus RAG Vector Ingestion Pipeline

## Overview
This guide provides instructions for setting up and running the Docusaurus RAG vector ingestion pipeline. The pipeline crawls your Docusaurus site, extracts content, generates embeddings using Cohere, and stores them in Qdrant Cloud.

## Prerequisites
- Python 3.11 or higher
- uv package manager
- Cohere API key
- Qdrant Cloud API key and URL
- Access to the Docusaurus site (default: http://localhost:3000/)

## Setup Instructions

### 1. Create Backend Directory
```bash
mkdir backend
cd backend
```

### 2. Initialize Project with uv
```bash
uv init
```

### 3. Install Dependencies
```bash
uv add requests beautifulsoup4 cohere qdrant-client python-dotenv
```

### 4. Create Environment File
Create a `.env` file with the following content:
```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
DOCS_URL=http://localhost:3000/
```

## Pipeline Functions Overview

The main.py file will contain these key functions:

### `get_all_urls(base_url)`
- Discovers all accessible URLs on the Docusaurus site
- Uses breadth-first crawling approach
- Respects robots.txt and implements rate limiting

### `extract_text_from_url(url)`
- Fetches content from a single URL
- Extracts clean text content from HTML
- Removes navigation, headers, and other non-content elements
- Preserves document title and section information

### `chunk_text(text, chunk_size=500, overlap=50)`
- Divides long text into smaller chunks
- Maintains sentence boundaries when possible
- Adds appropriate overlap between chunks
- Preserves context across chunk boundaries

### `embed(texts)`
- Generates Cohere embeddings for text chunks
- Handles rate limiting and API errors
- Returns embedding vectors with consistent dimensions

### `create_collection(collection_name="rag_embeddings")`
- Creates or connects to Qdrant collection
- Sets up proper vector dimensions and configuration
- Defines payload schema for metadata storage

### `save_chunk_to_qdrant(chunk_data, embedding)`
- Stores text chunk and embedding in Qdrant
- Saves metadata (URL, title, section) as payload
- Handles duplicate detection and updates

## Running the Pipeline

### 1. Execute the Main Function
```bash
python main.py
```

### 2. Monitor the Process
- The pipeline will crawl all URLs starting from the base URL
- Content will be extracted, chunked, and embedded
- Results will be stored in Qdrant with rich metadata

### 3. Verify Results
- Check Qdrant Cloud dashboard for stored embeddings
- Verify that metadata includes URL, title, and section information
- Test retrieval with a sample query to confirm functionality

## Configuration Options

### Environment Variables
- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_API_KEY`: Your Qdrant Cloud API key
- `QDRANT_URL`: Your Qdrant Cloud cluster URL
- `DOCS_URL`: Base URL of your Docusaurus site
- `CHUNK_SIZE`: Size of text chunks (default: 500 words)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50 words)
- `RATE_LIMIT_DELAY`: Delay between requests in seconds (default: 1)

## Troubleshooting

### Common Issues
- API rate limits: The pipeline includes built-in delays to respect rate limits
- Network timeouts: The pipeline has retry mechanisms for network issues
- Invalid URLs: The pipeline will skip invalid URLs and continue processing
- Content extraction issues: The pipeline handles malformed HTML gracefully

### Logging
- All operations are logged for debugging and monitoring
- Error messages provide specific details for troubleshooting
- Process statistics are available for performance monitoring