"""
Configuration management for the RAG Agent Service.

This module handles environment variables and service configuration
with validation and secure loading.
"""

import os
import re
from typing import List, Optional
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


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
        import logging
        logging.getLogger(__name__).info(mask_sensitive_info(str(msg)), *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        import logging
        logging.getLogger(__name__).error(mask_sensitive_info(str(msg)), *args, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        import logging
        logging.getLogger(__name__).warning(mask_sensitive_info(str(msg)), *args, **kwargs)

    @staticmethod
    def debug(msg, *args, **kwargs):
        import logging
        logging.getLogger(__name__).debug(mask_sensitive_info(str(msg)), *args, **kwargs)


class AgentConfig(BaseModel):
    """
    Configuration model for the RAG Agent Service.
    """
    # OpenAI configuration
    openai_api_key: str
    openai_assistant_id: Optional[str] = None
    model_name: str = "gpt-4-1106-preview"

    # Cohere configuration (for consistency with previous features)
    cohere_api_key: Optional[str] = None

    # OpenRouter configuration
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = "openai/gpt-3.5-turbo"

    # Qdrant configuration
    qdrant_api_key: str
    qdrant_url: str
    qdrant_collection_name: str = "rag_embeddings"

    # Retrieval configuration
    retrieval_threshold: float = 0.5
    max_context_chunks: int = 5
    max_tokens: int = 1000
    temperature: float = 0.7

    # Service configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS configuration
    allowed_origins: Optional[list] = None
    allowed_origin_regex: Optional[str] = None

    # Validation for API keys
    @field_validator('openai_api_key', 'qdrant_api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('API key cannot be empty')
        return v

    # Validation for URLs
    @field_validator('qdrant_url')
    @classmethod
    def validate_url(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('URL cannot be empty')
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    # Validation for thresholds
    @field_validator('retrieval_threshold')
    @classmethod
    def validate_retrieval_threshold(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Retrieval threshold must be between 0 and 1')
        return v

    # Validation for temperature
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v

    # Validation for max tokens
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        if v <= 0:
            raise ValueError('Max tokens must be positive')
        return v

    # Validation for max context chunks
    @field_validator('max_context_chunks')
    @classmethod
    def validate_max_context_chunks(cls, v):
        if v <= 0:
            raise ValueError('Max context chunks must be positive')
        return v


def validate_environment_variables() -> List[str]:
    """
    Validate that all required environment variables are properly configured.

    Returns:
        List of validation errors found
    """
    errors = []

    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "QDRANT_API_KEY", "QDRANT_URL"]

    for var in required_vars:
        value = os.getenv(var)
        if not value or len(value.strip()) == 0:
            errors.append(f"Missing or empty required environment variable: {var}")

    # Validate URL format
    qdrant_url = os.getenv("QDRANT_URL", "")
    if qdrant_url and not qdrant_url.startswith(("http://", "https://")):
        errors.append("QDRANT_URL must start with http:// or https://")

    # Validate numeric values
    try:
        retrieval_threshold = float(os.getenv("RETRIEVAL_THRESHOLD", "0.5"))
        if not 0 <= retrieval_threshold <= 1:
            errors.append("RETRIEVAL_THRESHOLD must be between 0 and 1")
    except ValueError:
        errors.append("RETRIEVAL_THRESHOLD must be a valid number")

    try:
        max_context_chunks = int(os.getenv("MAX_CONTEXT_CHUNKS", "5"))
        if max_context_chunks <= 0:
            errors.append("MAX_CONTEXT_CHUNKS must be a positive integer")
    except ValueError:
        errors.append("MAX_CONTEXT_CHUNKS must be a valid integer")

    try:
        max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        if max_tokens <= 0:
            errors.append("MAX_TOKENS must be a positive integer")
    except ValueError:
        errors.append("MAX_TOKENS must be a valid integer")

    try:
        temperature = float(os.getenv("TEMPERATURE", "0.7"))
        if not 0 <= temperature <= 2:
            errors.append("TEMPERATURE must be between 0 and 2")
    except ValueError:
        errors.append("TEMPERATURE must be a valid number")

    try:
        port = int(os.getenv("PORT", "8000"))
        if port <= 0 or port > 65535:
            errors.append("PORT must be between 1 and 65535")
    except ValueError:
        errors.append("PORT must be a valid integer")

    return errors


def get_config() -> AgentConfig:
    """
    Load and validate configuration from environment variables.

    Returns:
        AgentConfig: Validated configuration object

    Raises:
        ValueError: If required configuration is missing or invalid
    """
    # Validate environment variables
    validation_errors = validate_environment_variables()

    if validation_errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in validation_errors)
        raise ValueError(error_msg)

    # Create config object with environment values
    config = AgentConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
        model_name=os.getenv("MODEL_NAME", "gpt-4-1106-preview"),
        cohere_api_key=os.getenv("COHERE_API_KEY"),  # Added for consistency with previous features
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        qdrant_url=os.getenv("QDRANT_URL"),
        qdrant_collection_name=os.getenv("QDRANT_COLLECTION_NAME", "rag_embeddings"),
        retrieval_threshold=float(os.getenv("RETRIEVAL_THRESHOLD", "0.5")),
        max_context_chunks=int(os.getenv("MAX_CONTEXT_CHUNKS", "5")),
        max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        allowed_origins=os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"],
        allowed_origin_regex=os.getenv("ALLOWED_ORIGIN_REGEX")
    )

    # Log successful configuration loading without exposing sensitive values
    SecureLogger.info("Configuration loaded successfully with required environment variables")

    return config


# Global configuration instance
config = get_config()