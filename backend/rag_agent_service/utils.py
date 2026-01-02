"""
Utility functions for the RAG Agent Service.

This module contains helper functions for text embedding,
API interaction, and other utility operations.
"""

import logging
import re
import time
import random
from typing import List
import cohere
from openai import OpenAI, RateLimitError, APIConnectionError, APITimeoutError
from limits import storage, strategies
from .config import config


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


# Initialize rate limiters for API calls
rate_storage = storage.MemoryStorage()
rate_limiter = strategies.FixedWindowRateLimiter(rate_storage)


def rate_limit_embedding():
    """
    Decorator to enforce rate limiting for embedding API calls (Cohere/OpenAI).
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check rate limit (3000 requests per hour for Cohere)
            from limits import RateLimitItemPerMinute

            # Create rate limit item (50 requests per minute as example)
            rate_item = RateLimitItemPerMinute(50)

            # Check if we're within the rate limit
            if not rate_limiter.hit(rate_item, "embedding_api_call"):
                logger.warning(f"Rate limit exceeded for {func.__name__}. Waiting before retry...")
                # Wait a bit before trying again
                time.sleep(1)
                # Try again after delay
                if not rate_limiter.hit(rate_item, "embedding_api_call"):
                    logger.error(f"Rate limit still exceeded for {func.__name__}. Raising exception.")
                    raise Exception("Rate limit exceeded for embedding API calls")

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
                except (RateLimitError, APIConnectionError, APITimeoutError, ConnectionError) as e:
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


# Global variable to store the active embedding function
_active_embed_function = None


def get_embedding_function():
    """
    Return the appropriate embedding function based on configuration.
    For consistency with the existing ingestion pipeline, we'll use Cohere if available.
    """
    global _active_embed_function

    if _active_embed_function is not None:
        return _active_embed_function

    # For consistency with the original pipeline that used Cohere,
    # we prefer Cohere for embedding if the API key is available
    if config.cohere_api_key:
        _active_embed_function = _embed_text_cohere
    else:
        _active_embed_function = _embed_text_openai

    return _active_embed_function


@retry_on_failure(max_retries=3, base_delay=1.0, max_delay=30.0, backoff_factor=2.0)
@rate_limit_embedding()
def _embed_text_cohere(text: str) -> List[float]:
    """
    Generate embedding for text using Cohere (consistent with previous features).

    Args:
        text: The text to embed

    Returns:
        List of floats representing the embedding vector
    """
    try:
        logger.info(f"Generating embedding for text: {text[:50]}...")

        # Use Cohere for embedding (consistent with original ingestion pipeline)
        co = cohere.Client(config.cohere_api_key)

        response = co.embed(
            texts=[text],
            model="embed-english-v3.0",  # Same model used in ingestion
            input_type="search_query"    # Specify this is a search query (vs search_document in ingestion)
        )

        if response and response.embeddings and len(response.embeddings) > 0:
            logger.info(f"Successfully generated Cohere embedding for text: {text[:50]}...")
            return response.embeddings[0]  # Return the first (and only) embedding
        else:
            logger.error("Failed to generate Cohere embedding: No embeddings returned")
            raise ValueError("Failed to generate Cohere embedding: No embeddings returned")

    except Exception as e:
        logger.error(f"Error generating Cohere embedding for text: {e}")
        raise


@retry_on_failure(max_retries=3, base_delay=1.0, max_delay=30.0, backoff_factor=2.0)
@rate_limit_embedding()
def _embed_text_openai(text: str) -> List[float]:
    """
    Generate embedding using OpenAI API.

    Args:
        text: The text to embed

    Returns:
        List of floats representing the embedding vector
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.openai_api_key)

        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"  # Using OpenAI's embedding model
        )

        embedding = response.data[0].embedding
        logger.info(f"Generated OpenAI embedding for text: {text[:50]}...")
        return embedding

    except Exception as e:
        logger.error(f"Error generating OpenAI embedding for text: {e}")
        raise


# Create a global embedding function
embed_text = get_embedding_function()