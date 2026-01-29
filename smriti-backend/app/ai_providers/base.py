"""
Abstract base class for AI providers.

All AI providers must implement this interface to ensure consistent behavior.
"""

from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator
from dataclasses import dataclass


@dataclass
class ModelInfo:
    """Information about the AI model being used"""
    provider: str
    model_name: str
    supports_tts: bool
    max_tokens: int
    context_window: int


class AIProviderError(Exception):
    """Base exception for AI provider errors"""

    def __init__(
        self,
        message: str,
        provider: str,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.provider = provider
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.provider}] {self.message}"


class AIProviderRateLimitError(AIProviderError):
    """Raised when API rate limit is exceeded"""
    pass


class AIProviderAuthError(AIProviderError):
    """Raised when authentication fails"""
    pass


class AIProviderUnavailableError(AIProviderError):
    """Raised when the provider service is unavailable"""
    pass


class AIProviderInvalidResponseError(AIProviderError):
    """Raised when the provider returns an invalid or empty response"""
    pass


class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    All AI providers (OpenAI, Anthropic, Local, etc.) must implement this interface.
    This ensures consistent behavior and allows easy switching between providers.
    """

    @abstractmethod
    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a text completion.

        Args:
            system_prompt: System instructions for the AI
            user_prompt: User's request/prompt
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0-1.0)

        Returns:
            Generated text response

        Raises:
            AIProviderError: If generation fails
        """
        pass

    @abstractmethod
    async def generate_completion_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Generate a streaming text completion.

        Args:
            system_prompt: System instructions for the AI
            user_prompt: User's request/prompt
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0-1.0)

        Yields:
            Text chunks as they are generated

        Raises:
            AIProviderError: If generation fails
        """
        pass

    @abstractmethod
    async def generate_tts(
        self,
        text: str,
        voice: str = "nova",
        speed: float = 1.0
    ) -> bytes:
        """
        Generate text-to-speech audio.

        Args:
            text: Text to convert to speech
            voice: Voice identifier
            speed: Playback speed multiplier (0.25-4.0)

        Returns:
            Audio bytes (MP3 format)

        Raises:
            AIProviderError: If TTS generation fails
            NotImplementedError: If provider doesn't support TTS
        """
        pass

    @abstractmethod
    def get_model_info(self) -> ModelInfo:
        """
        Get information about the current model.

        Returns:
            ModelInfo with provider and model details
        """
        pass

    @abstractmethod
    def get_available_voices(self) -> list[str]:
        """
        Get list of available TTS voices.

        Returns:
            List of voice identifiers
        """
        pass

    def validate_response(self, response: str) -> bool:
        """
        Validate that AI response meets quality standards.

        Override this method to add custom validation logic.

        Args:
            response: The AI-generated response

        Returns:
            True if response is valid, False otherwise
        """
        if not response or not response.strip():
            return False

        # Check for red flags that indicate inappropriate response
        red_flags = [
            "you should immediately",
            "you must urgently",
            "seek professional help",
            "i diagnose",
            "as your therapist"
        ]

        response_lower = response.lower()
        return not any(flag in response_lower for flag in red_flags)
