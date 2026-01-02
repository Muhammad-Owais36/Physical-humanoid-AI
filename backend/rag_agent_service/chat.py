"""
Chat service module for handling chat-specific functionality in the RAG Agent Service.

This module provides services for managing chat conversations, processing messages,
and integrating with the existing RAG functionality.
"""

import logging
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .models import ChatRequest, ChatResponse, ChatMessage, ChatSession, QuestionRequest, QuestionResponse
from .orchestrator import get_orchestrator
from .config import config


class ChatService:
    """
    Service class for handling chat functionality.
    """

    def __init__(self, max_session_age_minutes: int = 30):
        """
        Initialize the chat service.

        Args:
            max_session_age_minutes: Maximum age of a session before it's considered expired (in minutes)
        """
        self.orchestrator = get_orchestrator()
        self.sessions: Dict[str, ChatSession] = {}
        self.max_session_age_minutes = max_session_age_minutes
        self.logger = logging.getLogger(__name__)

    def create_session(self, user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> ChatSession:
        """
        Create a new chat session.

        Args:
            user_id: Optional identifier for the user
            metadata: Optional metadata for the session

        Returns:
            ChatSession: The newly created chat session
        """
        session = ChatSession(
            user_id=user_id,
            metadata=metadata
        )
        self.sessions[session.id] = session
        self.logger.info(f"Created new chat session: {session.id}")
        return session

    def is_session_expired(self, session: ChatSession) -> bool:
        """
        Check if a session has expired based on the max session age.

        Args:
            session: The session to check

        Returns:
            bool: True if the session is expired, False otherwise
        """
        import datetime
        from datetime import timezone

        max_age = datetime.timedelta(minutes=self.max_session_age_minutes)
        current_time = datetime.datetime.now(timezone.utc) if session.updated_at.tzinfo else datetime.datetime.now()
        time_since_update = current_time - session.updated_at

        return time_since_update > max_age

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Retrieve a chat session by ID, checking if it's expired.

        Args:
            session_id: The ID of the session to retrieve

        Returns:
            ChatSession: The chat session if found and not expired, None otherwise
        """
        session = self.sessions.get(session_id)
        if session and self.is_session_expired(session):
            # Remove expired session
            del self.sessions[session_id]
            self.logger.info(f"Removed expired session: {session_id}")
            return None
        return session

    def cleanup_expired_sessions(self):
        """
        Remove all expired sessions from memory.
        """
        expired_sessions = []
        current_time = datetime.datetime.now()

        for session_id, session in self.sessions.items():
            if self.is_session_expired(session):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]
            self.logger.info(f"Cleaned up expired session: {session_id}")

        return len(expired_sessions)

    def add_message_to_session(self, session_id: str, message: ChatMessage) -> ChatSession:
        """
        Add a message to a chat session.

        Args:
            session_id: The ID of the session to add the message to
            message: The message to add

        Returns:
            ChatSession: The updated chat session

        Raises:
            ValueError: If the session doesn't exist
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} does not exist")

        session.messages.append(message)
        session.updated_at = datetime.now()
        return session

    def process_chat_message(self, chat_request: ChatRequest) -> ChatResponse:
        """
        Process a chat message by integrating with the RAG orchestrator.

        Args:
            chat_request: The incoming chat request

        Returns:
            ChatResponse: The response to the chat message
        """
        # Create a QuestionRequest from the ChatRequest for the existing orchestrator
        question_request = QuestionRequest(
            question=chat_request.message,
            user_id=chat_request.user_id,
            session_id=chat_request.session_id,
            metadata=chat_request.metadata
        )

        # Process the question through the orchestrator
        # The orchestrator returns (answer, retrieved_chunks) as a tuple
        answer, retrieved_chunks = self.orchestrator.process_question(question_request)

        # Extract sources from retrieved chunks
        sources = list(set(chunk.metadata.get('url', '') for chunk in retrieved_chunks if chunk.metadata.get('url')))
        sources = [s for s in sources if s]  # Remove empty strings

        # Calculate a basic confidence score based on similarity scores
        confidence_score = 0.0
        if retrieved_chunks:
            avg_similarity = sum(chunk.similarity_score for chunk in retrieved_chunks) / len(retrieved_chunks)
            confidence_score = min(1.0, avg_similarity * 1.5)  # Boost slightly to reflect agent processing

        # Create ChatResponse from the answer and retrieved chunks
        chat_response = ChatResponse(
            message=answer,
            session_id=chat_request.session_id or "unknown",
            sources=sources,
            request_id=str(uuid.uuid4())  # Generate a new request ID for the chat response
        )

        # If we have a session_id, add messages to the session
        if chat_request.session_id:
            try:
                # Add user message to session
                user_message = ChatMessage(
                    role="user",
                    content=chat_request.message
                )
                self.add_message_to_session(chat_request.session_id, user_message)

                # Add assistant message to session
                assistant_message = ChatMessage(
                    role="assistant",
                    content=answer
                )
                self.add_message_to_session(chat_request.session_id, assistant_message)
            except ValueError:
                # Session doesn't exist, create it
                session = self.create_session(
                    user_id=chat_request.user_id,
                    metadata=chat_request.metadata
                )
                # Update the response with the new session ID
                chat_response.session_id = session.id

                # Add messages to the new session
                user_message = ChatMessage(
                    role="user",
                    content=chat_request.message
                )
                self.add_message_to_session(session.id, user_message)

                assistant_message = ChatMessage(
                    role="assistant",
                    content=answer
                )
                self.add_message_to_session(session.id, assistant_message)

        return chat_response

    def process_question_with_context(self, question_request: QuestionRequest) -> QuestionResponse:
        """
        Process a question with additional context from the chat session.

        Args:
            question_request: The incoming question request

        Returns:
            QuestionResponse: The response to the question with context
        """
        # For now, we'll use the existing orchestrator directly
        # In the future, we could enhance this to use conversation context
        answer, retrieved_chunks = self.orchestrator.process_question(question_request)

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
            question=question_request.question,
            retrieved_chunks=retrieved_chunks,
            confidence_score=confidence_score,
            sources=sources,
            request_id=question_request.metadata.get('request_id') if question_request.metadata else None
        )

        return response


# Global chat service instance
_chat_service = None


def get_chat_service() -> ChatService:
    """
    Get the global chat service instance.

    Returns:
        ChatService: The chat service instance
    """
    global _chat_service
    if _chat_service is None:
        # Get session timeout from config, default to 30 minutes if not specified
        max_session_age = getattr(config, 'max_session_age_minutes', 30)
        _chat_service = ChatService(max_session_age_minutes=max_session_age)
    return _chat_service