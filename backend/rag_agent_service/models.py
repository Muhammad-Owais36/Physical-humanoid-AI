"""
Pydantic models for request/response validation in the RAG Agent Service.

This module defines the data structures for API requests and responses
with proper validation and serialization.
"""

import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class QuestionRequest(BaseModel):
    """
    Model for incoming question requests.
    """
    question: str = Field(..., min_length=1, max_length=2000, description="The user's question text")
    user_id: Optional[str] = Field(default=None, description="Identifier for the user (for tracking purposes)")
    session_id: Optional[str] = Field(default=None, description="Session identifier for conversation context")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the request")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the key concepts in the book?",
                "user_id": "user123",
                "session_id": "session456",
                "metadata": {"source": "web", "priority": "high"}
            }
        }


class RetrievedChunk(BaseModel):
    """
    Model for content chunks retrieved from Qdrant.
    """
    id: str = Field(..., description="Unique identifier from Qdrant")
    content: str = Field(..., description="Original chunk content from Qdrant")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score from vector search")
    metadata: Dict[str, Any] = Field(..., description="Original metadata from Qdrant (URL, title, section, etc.)")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score of relevance to the question (0.0-1.0)")
    used_in_response: bool = Field(default=False, description="Whether this chunk was used in the final response")


class QuestionResponse(BaseModel):
    """
    Model for outgoing question responses.
    """
    answer: str = Field(..., description="The agent's answer to the question")
    question: str = Field(..., description="The original question for reference")
    retrieved_chunks: List[RetrievedChunk] = Field(default=[], description="List of content chunks used to generate the answer")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence level in the answer (0.0-1.0)")
    sources: List[str] = Field(default=[], description="List of sources cited in the answer")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the response was generated")
    request_id: Optional[str] = Field(default=None, description="Reference to the original request")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The key concepts include...",
                "question": "What are the key concepts in the book?",
                "retrieved_chunks": [
                    {
                        "id": "chunk123",
                        "content": "The book discusses several key concepts...",
                        "similarity_score": 0.85,
                        "metadata": {"url": "http://example.com/page1", "title": "Introduction", "section": "overview"},
                        "relevance_score": 0.9,
                        "used_in_response": True
                    }
                ],
                "confidence_score": 0.9,
                "sources": ["http://example.com/page1"],
                "timestamp": "2025-12-19T10:00:00Z",
                "request_id": "req789"
            }
        }


class APIError(BaseModel):
    """
    Model for API error responses.
    """
    error_code: str = Field(..., description="Standardized error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the error occurred")
    request_id: Optional[str] = Field(default=None, description="Reference to the request that caused the error")


class HealthCheckResponse(BaseModel):
    """
    Model for health check responses.
    """
    status: str = Field(..., description="Health status of the service")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the health check was performed")
    version: str = Field(default="0.1.0", description="Version of the service")


class ChatMessage(BaseModel):
    """
    Model for individual chat messages in a conversation.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the message")
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the message was created")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the message")


class ChatSession(BaseModel):
    """
    Model for a chat session containing multiple messages.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the session")
    user_id: Optional[str] = Field(default=None, description="Identifier for the user")
    messages: List[ChatMessage] = Field(default=[], description="List of messages in the session")
    created_at: datetime = Field(default_factory=datetime.now, description="When the session was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the session was last updated")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the session")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "session123",
                "user_id": "user123",
                "messages": [
                    {
                        "id": "msg1",
                        "role": "user",
                        "content": "Hello, what can you help me with?",
                        "timestamp": "2025-12-19T10:00:00Z"
                    },
                    {
                        "id": "msg2",
                        "role": "assistant",
                        "content": "I can answer questions about the book content.",
                        "timestamp": "2025-12-19T10:00:01Z"
                    }
                ],
                "created_at": "2025-12-19T10:00:00Z",
                "updated_at": "2025-12-19T10:00:01Z"
            }
        }


class ChatRequest(BaseModel):
    """
    Model for incoming chat requests.
    """
    message: str = Field(..., min_length=1, max_length=2000, description="The user's message text")
    session_id: Optional[str] = Field(default=None, description="Session identifier for conversation context")
    user_id: Optional[str] = Field(default=None, description="Identifier for the user (for tracking purposes)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the request")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What are the key concepts in the book?",
                "session_id": "session456",
                "user_id": "user123",
                "metadata": {"source": "web", "priority": "high"}
            }
        }


class ChatResponse(BaseModel):
    """
    Model for outgoing chat responses.
    """
    message: str = Field(..., description="The assistant's response message")
    session_id: str = Field(..., description="Session identifier for conversation context")
    sources: List[str] = Field(default=[], description="List of sources cited in the response")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the response was generated")
    request_id: Optional[str] = Field(default=None, description="Reference to the original request")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the response")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "The key concepts include...",
                "session_id": "session456",
                "sources": ["http://example.com/page1"],
                "timestamp": "2025-12-19T10:00:00Z",
                "request_id": "req789",
                "metadata": {"processing_time": 1.234}
            }
        }