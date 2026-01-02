# RAG Agent Service

A service that integrates OpenAI Agents SDK with Qdrant for context-aware question answering over book content.

## Overview

This service provides a REST API that allows users to ask questions about book content and receive contextually relevant answers. The service retrieves relevant content from a Qdrant vector database and uses OpenAI's language models to generate helpful responses.

## Features

- Context-aware question answering using RAG (Retrieval Augmented Generation)
- Integration with OpenAI for response generation
- Vector similarity search with Qdrant
- Support for Cohere embeddings (with fallback to OpenAI)
- Secure configuration with environment variables
- Rate limiting and retry mechanisms
- Performance monitoring and logging
- Graceful error handling

## Prerequisites

- Python 3.11+
- OpenAI API key
- Qdrant Cloud account and API key
- (Optional) Cohere API key for embeddings

## Installation

1. Clone the repository
2. Navigate to the backend directory: `cd backend`
3. Install dependencies: `pip install -e .`
4. Create a `.env` file with your configuration (see `.env.example`)

## Configuration

Create a `.env` file in the backend directory with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ASSISTANT_ID=optional_assistant_id
MODEL_NAME=gpt-4-1106-preview  # or your preferred model

# Cohere Configuration (optional, for embeddings)
COHERE_API_KEY=your_cohere_api_key_here

# Qdrant Configuration
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=your_qdrant_url_here
QDRANT_COLLECTION_NAME=rag_embeddings

# Retrieval Configuration
RETRIEVAL_THRESHOLD=0.5
MAX_CONTEXT_CHUNKS=5
MAX_TOKENS=1000
TEMPERATURE=0.7

# Service Configuration
HOST=0.0.0.0
PORT=8000
```

## Usage

### Running the Service

```bash
cd backend
uvicorn rag_agent_service.main:app --host 0.0.0.0 --port 8000
```

Or run directly:

```bash
cd backend/rag_agent_service
python main.py
```

### API Endpoints

#### Health Check
```
GET /
```
Returns: `{"message": "RAG Agent Service is running"}`

#### Health Status
```
GET /health
```
Returns: `{"status": "healthy"}`

#### Ask a Question
```
POST /api/v1/ask
```

Request body:
```json
{
  "question": "Your question here",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id",
  "metadata": {}
}
```

Response:
```json
{
  "answer": "Generated answer",
  "question": "Original question",
  "retrieved_chunks": [...],
  "confidence_score": 0.8,
  "sources": [...],
  "request_id": "unique_request_id"
}
```

## Architecture

The service consists of several key components:

- **main.py**: FastAPI application with API endpoints
- **config.py**: Configuration management with environment variables
- **models.py**: Pydantic models for request/response validation
- **agent.py**: OpenAI agent integration
- **retrieval.py**: Qdrant vector retrieval logic
- **orchestrator.py**: Agent orchestration with context injection
- **utils.py**: Utility functions for text embedding

## Error Handling

The service includes comprehensive error handling:
- Validation of all inputs
- Graceful handling of API rate limits
- Retry mechanisms with exponential backoff
- Secure logging that masks sensitive information

## Performance

The service includes performance monitoring:
- Response time tracking
- Rate limiting to respect API quotas
- Context window management to optimize token usage

## Security

- All sensitive information is configured via environment variables
- Logging is secured to mask API keys and credentials
- Input validation is performed on all requests
- Rate limiting prevents abuse

## Development

To run tests (if available):
```bash
pytest
```

To run with auto-reload during development:
```bash
uvicorn rag_agent_service.main:app --reload
```

## Troubleshooting

- Ensure all required environment variables are set
- Verify Qdrant collection exists and contains data
- Check that API keys are valid and have necessary permissions
- Monitor logs for error messages and performance issues

## License

[Specify license here]