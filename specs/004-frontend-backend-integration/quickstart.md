# Quickstart: Frontend and Backend Integration for Local RAG Chatbot

## Overview
This guide provides instructions for setting up and running the integrated frontend and backend for the RAG chatbot service in a local development environment.

## Prerequisites
- Node.js 18+ (for Docusaurus frontend)
- Python 3.11+ (for FastAPI backend)
- pnpm package manager
- Access to the existing RAG agent service backend
- Valid OpenAI and Qdrant API keys

## Setup Instructions

### 1. Clone and Navigate to Repository
```bash
git clone [repository-url]
cd [repository-name]
```

### 2. Set Up Backend Service
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Configure Backend Environment
Create a `.env` file in the backend directory with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_COLLECTION_NAME=rag_embeddings
MODEL_NAME=gpt-4-1106-preview
RETRIEVAL_THRESHOLD=0.5
MAX_CONTEXT_CHUNKS=5
MAX_TOKENS=1000
TEMPERATURE=0.7
```

### 4. Start Backend Service
```bash
# From the backend directory
uvicorn rag_agent_service.main:app --reload --port 8000
```

### 5. Set Up Frontend (Docusaurus)
```bash
# In a new terminal, navigate to the docs directory
cd docs  # or wherever your Docusaurus project is located

# Install dependencies
pnpm install
```

### 6. Configure Frontend API Connection
Update the Docusaurus configuration to connect to your backend service by adding the API endpoint configuration to `docusaurus.config.js`:

```js
// Add to docusaurus.config.js
module.exports = {
  // ... other config
  customFields: {
    backendApiUrl: process.env.BACKEND_API_URL || 'http://localhost:8000',
  },
};
```

### 7. Start Frontend Development Server
```bash
# From the docs directory
pnpm start
```

## Integration Components Overview

### Backend Extensions
- `/api/v1/chat` - New chat-specific endpoint for frontend communication
- Enhanced CORS configuration to allow frontend requests
- Environment-based API endpoint configuration

### Frontend Components
- `ChatInterface` - React component for the chat interface
- `ApiClient` - Service for communicating with the backend API
- CSS styling for the chat interface

## Running the Integrated Service

### 1. Both Services Running
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

### 2. Using the Chat Interface
- Navigate to the book page in the Docusaurus frontend
- Use the chat interface to ask questions about the book content
- View responses with source citations from the RAG system

### 3. Development Workflow
- Frontend changes auto-reload at `http://localhost:3000`
- Backend changes auto-reload at `http://localhost:8000`
- API requests from frontend are proxied to backend

## API Endpoints

### POST /api/v1/chat
**Description**: Send a message to the RAG chatbot and receive a response

**Request Body**:
```json
{
  "message": "Your question here",
  "session_id": "optional session identifier"
}
```

**Response**:
```json
{
  "response": "The assistant's answer",
  "session_id": "session identifier",
  "sources": ["source1", "source2"],
  "confidence": 0.85,
  "timestamp": "2025-12-20T10:00:00Z",
  "retrieved_chunks": [
    {
      "id": "chunk_id",
      "content": "retrieved content",
      "similarity_score": 0.85
    }
  ]
}
```

## Configuration Options

### Environment Variables
- `BACKEND_API_URL`: URL of the backend service (default: http://localhost:8000)
- `CHAT_TIMEOUT`: Request timeout in seconds (default: 30)

### Development Settings
- Hot reloading enabled for both frontend and backend
- CORS configured for local development (all origins allowed)
- Detailed logging enabled for debugging

## Troubleshooting

### Common Issues
- **CORS errors**: Ensure backend CORS middleware allows frontend origin
- **API connection failures**: Verify backend service is running and accessible
- **Environment configuration**: Check that all required environment variables are set

### Logging
- Backend logs show API request/response details
- Frontend console shows API communication status
- Network tab in browser shows request/response details

## Testing the Integration

### Manual Testing
1. Start both frontend and backend services
2. Navigate to the frontend application
3. Submit a question in the chat interface
4. Verify the response appears with source citations
5. Check browser console and backend logs for any errors

### API Testing
Use curl or a tool like Postman to directly test the backend API:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the key concepts in the book?"
  }'
```