"""
AI Provider Factory

Creates and manages AI provider instances based on configuration.
Supports easy switching between providers via environment variables.
"""

from typing import Optional, Type
from functools import lru_cache
import logging

from app.ai_providers.base import AIProvider, AIProviderError

logger = logging.getLogger(__name__)


class AIProviderFactory:
    """
    Factory for creating AI provider instances.

    Supports:
    - openai: OpenAI GPT models with TTS
    - anthropic: Anthropic Claude models
    - local: Local Ollama models
    - mock: Mock provider for testing
    """

    _providers: dict[str, Type[AIProvider]] = {}
    _instances: dict[str, AIProvider] = {}

    @classmethod
    def register(cls, name: str, provider_class: Type[AIProvider]):
        """
        Register a new provider type.

        Args:
            name: Provider identifier
            provider_class: Provider class (must inherit from AIProvider)
        """
        if not issubclass(provider_class, AIProvider):
            raise ValueError(f"{provider_class} must inherit from AIProvider")
        cls._providers[name] = provider_class
        logger.debug(f"Registered AI provider: {name}")

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of registered provider names"""
        return list(cls._providers.keys())

    @classmethod
    def create(
        cls,
        provider_name: str,
        **kwargs
    ) -> AIProvider:
        """
        Create a new AI provider instance.

        Args:
            provider_name: Provider name (openai, anthropic, local, mock)
            **kwargs: Additional arguments passed to provider constructor

        Returns:
            Configured AIProvider instance

        Raises:
            AIProviderError: If provider is not supported or initialization fails
        """
        # Ensure providers are registered
        cls._ensure_registered()

        if provider_name not in cls._providers:
            available = ", ".join(cls.get_available_providers())
            raise AIProviderError(
                f"Unknown AI provider: '{provider_name}'. Available: {available}",
                provider=provider_name
            )

        try:
            provider_class = cls._providers[provider_name]
            return provider_class(**kwargs)
        except AIProviderError:
            raise
        except Exception as e:
            raise AIProviderError(
                f"Failed to create {provider_name} provider: {str(e)}",
                provider=provider_name,
                original_error=e
            )

    @classmethod
    def create_from_settings(cls) -> AIProvider:
        """
        Create provider based on application settings.

        Reads configuration from settings and creates the appropriate provider.
        """
        from app.config.settings import settings

        provider_name = getattr(settings, "AI_PROVIDER", "mock")

        if provider_name == "openai":
            api_key = getattr(settings, "OPENAI_API_KEY", None)
            model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
            tts_model = getattr(settings, "OPENAI_TTS_MODEL", "tts-1")
            default_voice = getattr(settings, "OPENAI_TTS_VOICE", "nova")

            return cls.create(
                "openai",
                api_key=api_key,
                model=model,
                tts_model=tts_model,
                default_voice=default_voice
            )

        elif provider_name == "anthropic":
            api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
            model = getattr(settings, "ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            openai_key = getattr(settings, "OPENAI_API_KEY", None)  # For TTS fallback

            return cls.create(
                "anthropic",
                api_key=api_key,
                model=model,
                openai_api_key=openai_key
            )

        elif provider_name == "local":
            base_url = getattr(settings, "LOCAL_MODEL_URL", "http://localhost:11434")
            model = getattr(settings, "LOCAL_MODEL_NAME", "llama3")
            openai_key = getattr(settings, "OPENAI_API_KEY", None)  # For TTS fallback

            return cls.create(
                "local",
                base_url=base_url,
                model=model,
                openai_api_key=openai_key
            )

        elif provider_name == "mock":
            return cls.create("mock")

        else:
            raise AIProviderError(
                f"Unknown AI_PROVIDER in settings: '{provider_name}'",
                provider=provider_name
            )

    @classmethod
    def _ensure_registered(cls):
        """Ensure all built-in providers are registered"""
        if cls._providers:
            return

        # Import and register providers
        from app.ai_providers.openai_provider import OpenAIProvider
        from app.ai_providers.anthropic_provider import AnthropicProvider
        from app.ai_providers.local_provider import LocalProvider
        from app.ai_providers.mock_provider import MockAIProvider

        cls.register("openai", OpenAIProvider)
        cls.register("anthropic", AnthropicProvider)
        cls.register("local", LocalProvider)
        cls.register("mock", MockAIProvider)


# Cached provider instance for dependency injection
_cached_provider: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    """
    Get a cached AI provider instance.

    This is the main entry point for getting an AI provider.
    The provider is cached to reuse connections and configuration.

    Usage:
        from app.ai_providers import get_ai_provider

        provider = get_ai_provider()
        response = await provider.generate_completion(...)
    """
    global _cached_provider

    if _cached_provider is None:
        _cached_provider = AIProviderFactory.create_from_settings()
        logger.info(
            f"Initialized AI provider: {_cached_provider.get_model_info().provider}"
        )

    return _cached_provider


def reset_ai_provider():
    """
    Reset the cached provider.

    Useful for testing or when configuration changes.
    """
    global _cached_provider
    _cached_provider = None


def set_ai_provider(provider: AIProvider):
    """
    Set a custom provider instance.

    Useful for testing with mock providers.

    Args:
        provider: AIProvider instance to use
    """
    global _cached_provider
    _cached_provider = provider
