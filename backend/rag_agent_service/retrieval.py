"""
Qdrant vector retrieval logic for the RAG Agent Service.

This module handles connection to Qdrant, vector similarity search,
and result formatting for the RAG system.
"""

import logging
import re
import time
import random
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse
from limits import storage, strategies
from .config import config
from .models import RetrievedChunk


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


logger = SecureLogger


# Initialize rate limiters for Qdrant API calls
rate_storage = storage.MemoryStorage()
rate_limiter = strategies.FixedWindowRateLimiter(rate_storage)


def rate_limit_qdrant():
    """
    Decorator to enforce rate limiting for Qdrant API calls.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check rate limit (100 requests per minute as example)
            from limits import RateLimitItemPerMinute

            # Create rate limit item (100 requests per minute as example)
            rate_item = RateLimitItemPerMinute(100)

            # Check if we're within the rate limit
            if not rate_limiter.hit(rate_item, "qdrant_api_call"):
                logger.warning(f"Rate limit exceeded for {func.__name__}. Waiting before retry...")
                # Wait a bit before trying again
                time.sleep(1)
                # Try again after delay
                if not rate_limiter.hit(rate_item, "qdrant_api_call"):
                    logger.error(f"Rate limit still exceeded for {func.__name__}. Raising exception.")
                    raise Exception("Rate limit exceeded for Qdrant API calls")

            # Execute the function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, backoff_factor: float = 2.0):
    """
    Decorator to retry a function on failure with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, UnexpectedResponse, TimeoutError) as e:
                    last_exception = e

                    if attempt == max_retries:
                        # Final attempt failed, raise the exception
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise e

                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.1)  # Add up to 10% jitter
                    total_delay = delay + jitter

                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {total_delay:.2f} seconds...")
                    time.sleep(total_delay)

            # This should never be reached, but included for completeness
            if last_exception:
                raise last_exception
        return wrapper
    return decorator


class VectorRetriever:
    """
    Wrapper class for Qdrant vector retrieval functionality.
    """

    def __init__(self):
        """
        Initialize the Qdrant client with connection validation.
        """
        # Validate required configuration
        if not config.qdrant_api_key or not config.qdrant_url:
            raise ValueError("QDRANT_API_KEY and QDRANT_URL environment variables are required")

        # Initialize Qdrant client
        self.client = QdrantClient(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
        )

        # Set collection name
        self.collection_name = config.qdrant_collection_name

        # Check if collection exists, create if it doesn't
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                logger.warning(f"Collection '{self.collection_name}' does not exist in Qdrant, creating it...")
                # Create the collection with appropriate vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),  # Assuming OpenAI embeddings
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Successfully connected to existing Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to connect to or create Qdrant collection: {e}")
            # Instead of raising an error, we'll make it optional so the app can run without Qdrant
            logger.warning("Qdrant is not available. The application will run but without RAG functionality.")
            self.qdrant_available = False
        else:
            self.qdrant_available = True

    @retry_on_failure(max_retries=3, base_delay=1.0, max_delay=30.0, backoff_factor=2.0)
    @rate_limit_qdrant()
    def retrieve_similar_chunks(self, query_embedding: List[float], limit: int = 5) -> List[RetrievedChunk]:
        """
        Retrieve similar content chunks from Qdrant based on the query embedding.

        Args:
            query_embedding: The embedding vector to search for similar items
            limit: Maximum number of results to return

        Returns:
            List of retrieved chunks with metadata and similarity scores
        """
        # If Qdrant is not available, return empty list
        if not self.qdrant_available:
            logger.warning("Qdrant not available, returning empty chunk list")
            return []

        try:
            # Perform the search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True,  # Include metadata/payload
                with_vectors=False  # Don't need the vectors themselves
            )

            # Format results to include content, metadata, and similarity scores
            retrieved_chunks = []
            for result in search_results:
                retrieved_chunk = RetrievedChunk(
                    id=result.id,
                    content=result.payload.get('content', ''),
                    similarity_score=result.score,
                    metadata={
                        'url': result.payload.get('url', ''),
                        'title': result.payload.get('title', ''),
                        'section': result.payload.get('section', ''),
                        'chunk_index': result.payload.get('chunk_index', 0),
                        'document_hash': result.payload.get('document_hash', ''),
                        'created_at': result.payload.get('created_at', '')
                    },
                    relevance_score=result.score,  # Using similarity score as relevance
                    used_in_response=False  # Will be set to True when used in response
                )
                retrieved_chunks.append(retrieved_chunk)

            logger.info(f"Successfully retrieved {len(retrieved_chunks)} results from Qdrant")
            return retrieved_chunks

        except Exception as e:
            logger.error(f"Failed to retrieve similar chunks from Qdrant: {e}")
            # Return empty list if there's an error, so the application can continue working
            return []

    @retry_on_failure(max_retries=2, base_delay=1.0, max_delay=10.0, backoff_factor=2.0)
    @rate_limit_qdrant()
    def validate_connection(self) -> bool:
        """
        Validate that the Qdrant connection is working.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try to get collections to test connection
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant connection validation failed: {e}")
            return False


# Global retriever instance
retriever = VectorRetriever()


def get_retriever() -> VectorRetriever:
    """
    Get the global retriever instance.

    Returns:
        VectorRetriever: The initialized retriever instance
    """
    return retriever