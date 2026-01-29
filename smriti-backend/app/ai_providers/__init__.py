"""
AI Provider Abstraction Layer

This module provides a unified interface for interacting with various AI providers
(OpenAI, Anthropic, local models). It allows easy switching between providers
without changing application code.

Usage:
    from app.ai_providers import get_ai_provider

    provider = get_ai_provider()
    response = await provider.generate_completion(
        system_prompt="You are a helpful assistant.",
        user_prompt="Hello!"
    )
"""

from app.ai_providers.base import (
    AIProvider,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderAuthError,
    AIProviderUnavailableError,
    ModelInfo
)
from app.ai_providers.factory import (
    AIProviderFactory,
    get_ai_provider
)

__all__ = [
    # Base classes
    "AIProvider",
    "ModelInfo",
    # Errors
    "AIProviderError",
    "AIProviderRateLimitError",
    "AIProviderAuthError",
    "AIProviderUnavailableError",
    # Factory
    "AIProviderFactory",
    "get_ai_provider"
]
