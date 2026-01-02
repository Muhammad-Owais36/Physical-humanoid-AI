"""
OpenAI agent integration for the RAG Agent Service.

This module handles OpenAI client initialization, assistant management,
and response generation with proper error handling.
"""

import logging
import re
import time
import random
from typing import List, Optional, Dict, Any
from openai import OpenAI, RateLimitError, APIConnectionError, APITimeoutError
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
                except (RateLimitError, APIConnectionError, APITimeoutError) as e:
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




class OpenAIAgent:
    """
    Wrapper class for OpenAI agent functionality.
    """

    def __init__(self):
        """
        Initialize the OpenAI client with API key validation.
        """
        # Validate API key is available (either OpenRouter or OpenAI)
        if not config.openrouter_api_key and not config.openai_api_key:
            raise ValueError("Either OPENROUTER_API_KEY or OPENAI_API_KEY environment variable is required")

        # Initialize OpenAI client with OpenRouter - prefer OpenRouter API key if available
        api_key = config.openrouter_api_key or config.openai_api_key
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"  # Support OpenRouter
        )

        # Set model - prefer OpenRouter model if available, fallback to default
        self.model = config.openrouter_model or 'openai/gpt-3.5-turbo'
        # Alternative: self.model = 'microsoft/wizardlm-2-8x22b'  # Another reliable OpenRouter model

        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

        logger.info("OpenAI agent (via OpenRouter) initialized successfully")

    @retry_on_failure(max_retries=3, base_delay=1.0, max_delay=30.0, backoff_factor=2.0)
    def create_completion(self, prompt: str, context_chunks: List[RetrievedChunk]) -> str:
        """
        Generate a completion using the OpenAI API with provided context.

        Args:
            prompt: The user's question or prompt
            context_chunks: List of retrieved content chunks to provide context

        Returns:
            Generated response from the OpenAI model
        """
        try:
            # Format context from retrieved chunks
            context_text = self._format_context(context_chunks)

            # Construct the full message with context (or without if no context available)
            if context_text and context_text != "No relevant context found.":
                system_message = f"""
                You are a helpful assistant that answers questions based on the provided context.
                The context contains information from book content that has been retrieved based on the user's question.
                Please provide accurate answers based on the context.

                Context:
                {context_text}
                """
            else:
                # If no context is available, use a simpler system message
                system_message = "You are a helpful AI assistant. Please answer the user's question to the best of your ability."

            # Create the completion request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Extract the response content
            answer = response.choices[0].message.content

            # Ensure we have a valid response
            if not answer:
                logger.warning("Received empty response from AI model")
                answer = "I received a response but it was empty. Please try asking your question again."

            logger.info(f"Generated completion for prompt: {prompt[:100]}...")
            return answer

        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise

    def _format_context(self, context_chunks: List[RetrievedChunk]) -> str:
        """
        Format retrieved chunks into a context string for the agent.

        Args:
            context_chunks: List of retrieved content chunks

        Returns:
            Formatted context string
        """
        if not context_chunks:
            return "No relevant context found."

        formatted_chunks = []
        for chunk in context_chunks:
            chunk_text = f"""
            Source: {chunk.metadata.get('url', 'Unknown source')}
            Title: {chunk.metadata.get('title', 'Untitled')}
            Section: {chunk.metadata.get('section', 'Unknown')}
            Content: {chunk.content}
            Similarity Score: {chunk.similarity_score}
            ---
            """
            formatted_chunks.append(chunk_text)

        return "\n".join(formatted_chunks)

   
# Global agent instance
agent = OpenAIAgent()


def get_agent() -> OpenAIAgent:
    """
    Get the global agent instance.

    Returns:
        OpenAIAgent: The initialized agent instance
    """
    return agent

