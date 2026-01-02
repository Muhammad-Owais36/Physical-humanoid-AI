"""
FastAPI application for the RAG Agent Service.

This service integrates OpenAI Agents SDK with Qdrant for context-aware
question answering over book content.
"""

import logging
import uuid
import re
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

# Import our modules
from .models import QuestionRequest, QuestionResponse, ChatRequest, ChatResponse
from .config import config
from .orchestrator import get_orchestrator
from .chat import get_chat_service


# Configure secure logging to mask sensitive information
def mask_sensitive_info(message: str) -> str:
    """
    Mask sensitive information in log messages.

    Args:
        message: The log message to mask

    Returns:
        The masked log message with sensitive info replaced
    """
    # Mask potential API keys (sequences of 32+ alphanumeric/hyphen/underscore characters)
    masked = re.sub(r'[A-Za-z0-9\-_]{32,}', '***MASKED***', message)
    # Mask potential URLs with credentials
    masked = re.sub(r'(https?://)[^@\s]+@', r'\1***MASKED***@', masked)
    return masked


class SecureLogger:
    """Wrapper for secure logging that masks sensitive information."""

    @staticmethod
    def info(msg, *args, **kwargs):
        logging.getLogger(__name__).info(mask_sensitive_info(str(msg)), *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        logging.getLogger(__name__).error(mask_sensitive_info(str(msg)), *args, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        logging.getLogger(__name__).warning(mask_sensitive_info(str(msg)), *args, **kwargs)

    @staticmethod
    def debug(msg, *args, **kwargs):
        logging.getLogger(__name__).debug(mask_sensitive_info(str(msg)), *args, **kwargs)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for graceful startup and shutdown.
    """
    # Startup
    SecureLogger.info("Starting RAG Agent Service")
    yield
    # Shutdown
    SecureLogger.info("Shutting down RAG Agent Service")


# Create FastAPI application instance
app = FastAPI(
    title="RAG Agent Service",
    description="A service that integrates OpenAI Agents SDK with Qdrant for context-aware question answering",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware with enhanced configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins or ["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    # Additional security headers for production
    allow_origin_regex=config.allowed_origin_regex,  # Optional regex for dynamic origins
    max_age=86400,  # Cache preflight requests for 24 hours
)

@app.get("/")
async def root():
    """
    Root endpoint to verify the service is running.
    """
    SecureLogger.info("Root endpoint accessed")
    return {"message": "RAG Agent Service is running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    SecureLogger.info("Health check endpoint accessed")
    return {"status": "healthy"}

@app.post("/api/v1/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Endpoint to submit a question and receive a context-aware answer.

    Args:
        request: QuestionRequest containing the user's question and optional metadata

    Returns:
        QuestionResponse containing the answer and supporting information
    """
    request_id = str(uuid.uuid4())
    SecureLogger.info(f"Processing question request {request_id}: {request.question[:100]}...")

    try:
        # Validate the request
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        if len(request.question) > 2000:  # Max length from models.py
            raise HTTPException(status_code=400, detail="Question is too long")

        # Get the orchestrator instance
        orchestrator = get_orchestrator()

        # Process the question through the orchestrator
        answer, retrieved_chunks = orchestrator.process_question(request)

        # Extract sources from retrieved chunks
        sources = list(set(chunk.metadata.get('url', '') for chunk in retrieved_chunks if chunk.metadata.get('url')))
        sources = [s for s in sources if s]  # Remove empty strings

        # Calculate a basic confidence score based on similarity scores
        confidence_score = 0.0
        if retrieved_chunks:
            avg_similarity = sum(chunk.similarity_score for chunk in retrieved_chunks) / len(retrieved_chunks)
            confidence_score = min(1.0, avg_similarity * 1.5)  # Boost slightly to reflect agent processing

        # Create response
        response = QuestionResponse(
            answer=answer,
            question=request.question,
            retrieved_chunks=retrieved_chunks,
            confidence_score=confidence_score,
            sources=sources,
            request_id=request_id
        )

        SecureLogger.info(f"Successfully processed question request {request_id}")
        return response

    except ValidationError as e:
        SecureLogger.error(f"Validation error for request {request_id}: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        SecureLogger.error(f"Error processing question request {request_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint for chat interactions with conversation context.

    Args:
        request: ChatRequest containing the user's message and optional session context

    Returns:
        ChatResponse containing the assistant's response and session information
    """
    request_id = str(uuid.uuid4())
    start_time = datetime.now()

    # Log the incoming request
    SecureLogger.info(f"Processing chat request {request_id} from user {request.user_id or 'unknown'} with session {request.session_id or 'none'}")
    SecureLogger.debug(f"Request details - Message: {request.message[:100]}..., User ID: {request.user_id}, Session ID: {request.session_id}")

    try:
        # Validate the request
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        if len(request.message) > 2000:  # Max length from models.py
            raise HTTPException(status_code=400, detail="Message is too long")

        # Get the chat service instance
        chat_service = get_chat_service()

        # Process the chat message through the chat service
        response = chat_service.process_chat_message(request)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Log successful response
        SecureLogger.info(f"Successfully processed chat request {request_id} in {processing_time:.2f}s")
        SecureLogger.debug(f"Response details - Message length: {len(response.message)}, Sources: {len(response.sources)}")

        return response

    except ValidationError as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        SecureLogger.error(f"Validation error for chat request {request_id} after {processing_time:.2f}s: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        SecureLogger.error(f"Error processing chat request {request_id} after {processing_time:.2f}s: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    SecureLogger.info("Starting RAG Agent Service")
    uvicorn.run(app, host="0.0.0.0", port=8000)