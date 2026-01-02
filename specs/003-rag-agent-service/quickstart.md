# Quickstart: RAG Agent Service with OpenAI Agents SDK and FastAPI

## Overview
This guide provides instructions for setting up and running the RAG agent service. The service integrates OpenAI Agents SDK with FastAPI and Qdrant to provide context-aware question answering over book content.

## Prerequisites
- Python 3.11 or higher
- uv package manager
- OpenAI API key
- Qdrant Cloud API key and URL (from previous features)
- Access to the existing "rag_embeddings" collection from previous features
- Existing book content already ingested in Qdrant

## Setup Instructions

### 1. Create RAG Agent Service Directory
```bash
mkdir backend/rag_agent_service
```

### 2. Initialize Project with uv
```bash
cd backend
uv init
```

### 3. Install Dependencies
```bash
uv add fastapi openai qdrant-client python-dotenv uvicorn pydantic
```

### 4. Create Environment File
Create a `.env` file with the following content:
```env
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_COLLECTION_NAME=rag_embeddings
OPENAI_ASSISTANT_ID=your_assistant_id_here
MODEL_NAME=gpt-4-1106-preview
RETRIEVAL_THRESHOLD=0.5
MAX_CONTEXT_CHUNKS=5
MAX_TOKENS=1000
TEMPERATURE=0.7
```

## Service Components Overview

The rag_agent_service package will contain these key modules:

### `main.py` - FastAPI Application
- API endpoints for question answering
- Request/response validation
- Error handling and logging

### `config.py` - Configuration Management
- Environment variable loading
- Configuration validation
- Service settings management

### `models.py` - Pydantic Models
- Request/response data models
- Validation schemas
- Type definitions

### `retrieval.py` - Qdrant Integration
- Vector search functionality
- Content retrieval logic
- Result formatting

### `agent.py` - OpenAI Agent Integration
- Assistant initialization
- Agent orchestration
- Response generation

### `orchestrator.py` - Workflow Management
- Request processing pipeline
- Context injection
- Agent interaction coordination

## Running the Service

### 1. Start the FastAPI Server
```bash
cd backend
uvicorn rag_agent_service.main:app --reload --port 8000
```

### 2. Test the Service
```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key concepts in the book?"
  }'
```

### 3. Monitor the Service
- Check logs for processing information
- Monitor response times and success rates
- Verify that retrieved content is being used appropriately

## API Endpoints

### POST /api/v1/ask
**Description**: Submit a question and receive a context-aware answer

**Request Body**:
```json
{
  "question": "Your question here",
  "user_id": "optional user identifier",
  "session_id": "optional session identifier"
}
```

**Response**:
```json
{
  "answer": "The agent's answer",
  "question": "Original question",
  "retrieved_chunks": [
    {
      "id": "chunk_id",
      "content": "retrieved content",
      "similarity_score": 0.85,
      "metadata": {}
    }
  ],
  "confidence_score": 0.9,
  "sources": ["source1", "source2"],
  "timestamp": "2025-12-19T10:00:00Z"
}
```

## Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `QDRANT_API_KEY`: Your Qdrant Cloud API key
- `QDRANT_URL`: Your Qdrant Cloud cluster URL
- `QDRANT_COLLECTION_NAME`: Name of collection to query (default: rag_embeddings)
- `OPENAI_ASSISTANT_ID`: ID of your OpenAI assistant
- `MODEL_NAME`: OpenAI model to use (default: gpt-4-1106-preview)
- `RETRIEVAL_THRESHOLD`: Minimum similarity score for retrieved content (default: 0.5)
- `MAX_CONTEXT_CHUNKS`: Maximum number of chunks to include in context (default: 5)
- `MAX_TOKENS`: Maximum tokens for agent responses (default: 1000)
- `TEMPERATURE`: Temperature setting for response creativity (default: 0.7)

### Service Settings
- Response timeout: 30 seconds
- Maximum question length: 2000 characters
- Maximum response length: 1000 tokens
- Rate limiting: 10 requests per minute per IP

## Troubleshooting

### Common Issues
- API rate limits: The service includes built-in rate limiting and retry mechanisms
- Network timeouts: The service has timeout handling and retry logic for network operations
- Invalid questions: The service validates input and returns appropriate error messages
- Qdrant connection issues: The service validates connection before processing

### Logging
- All operations are logged for debugging and monitoring
- Error messages provide specific details for troubleshooting
- Request/response metrics are available for performance analysis

## Performance Considerations

### Response Times
- Target response time: Under 10 seconds for typical queries
- Factors affecting performance: Qdrant retrieval speed, OpenAI API latency, context size
- Caching mechanisms can be implemented for frequently asked questions

### Scalability
- The service is designed to handle concurrent requests
- Consider load balancing for high-traffic scenarios
- Database connection pooling is handled automatically by the Qdrant client