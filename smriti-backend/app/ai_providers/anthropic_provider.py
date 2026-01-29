"""
Anthropic Claude API provider implementation.

Supports Claude models for text generation.
Note: Anthropic does not have native TTS - falls back to OpenAI if available.
"""

from typing import Optional, AsyncIterator
import logging

from app.ai_providers.base import (
    AIProvider,
    ModelInfo,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderAuthError,
    AIProviderUnavailableError,
    AIProviderInvalidResponseError
)

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider implementation"""

    # Model context windows
    CONTEXT_WINDOWS = {
        "claude-3-5-sonnet-20241022": 200000,
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000
    }

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        openai_api_key: Optional[str] = None  # For TTS fallback
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model to use for completions
            openai_api_key: Optional OpenAI key for TTS fallback
        """
        if not api_key:
            raise AIProviderAuthError(
                "Anthropic API key is required",
                provider="anthropic"
            )

        self.api_key = api_key
        self.model = model
        self.openai_api_key = openai_api_key
        self._client = None
        self._openai_provider = None

    @property
    def client(self):
        """Lazy initialization of Anthropic client"""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise AIProviderError(
                    "anthropic package not installed. Run: pip install anthropic",
                    provider="anthropic"
                )
        return self._client

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate completion using Anthropic API"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )

            if not response.content or not response.content[0].text:
                raise AIProviderInvalidResponseError(
                    "Anthropic returned empty response",
                    provider="anthropic"
                )

            return response.content[0].text.strip()

        except AIProviderError:
            raise
        except Exception as e:
            error_type = type(e).__name__

            if "RateLimitError" in error_type:
                raise AIProviderRateLimitError(
                    "Anthropic rate limit exceeded. Please try again later.",
                    provider="anthropic",
                    original_error=e
                )
            elif "AuthenticationError" in error_type:
                raise AIProviderAuthError(
                    "Anthropic authentication failed. Check your API key.",
                    provider="anthropic",
                    original_error=e
                )
            elif "APIConnectionError" in error_type:
                raise AIProviderUnavailableError(
                    "Anthropic API is unavailable. Please try again later.",
                    provider="anthropic",
                    original_error=e
                )
            else:
                logger.error(f"Anthropic error: {e}")
                raise AIProviderError(
                    f"Anthropic request failed: {str(e)}",
                    provider="anthropic",
                    original_error=e
                )

    async def generate_completion_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Generate streaming completion using Anthropic API"""
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise AIProviderError(
                f"Anthropic streaming failed: {str(e)}",
                provider="anthropic",
                original_error=e
            )

    async def generate_tts(
        self,
        text: str,
        voice: str = "nova",
        speed: float = 1.0
    ) -> bytes:
        """
        Generate TTS audio.

        Anthropic doesn't have native TTS, so we fall back to OpenAI if available.
        """
        if self.openai_api_key:
            # Lazy load OpenAI provider for TTS
            if self._openai_provider is None:
                from app.ai_providers.openai_provider import OpenAIProvider
                self._openai_provider = OpenAIProvider(
                    api_key=self.openai_api_key
                )

            return await self._openai_provider.generate_tts(text, voice, speed)

        raise NotImplementedError(
            "Anthropic does not support TTS. Configure OPENAI_API_KEY for TTS fallback."
        )

    def get_model_info(self) -> ModelInfo:
        """Get Anthropic model information"""
        return ModelInfo(
            provider="anthropic",
            model_name=self.model,
            supports_tts=self.openai_api_key is not None,
            max_tokens=4096,
            context_window=self.CONTEXT_WINDOWS.get(self.model, 200000)
        )

    def get_available_voices(self) -> list[str]:
        """Get available TTS voices (from OpenAI fallback)"""
        if self.openai_api_key:
            return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        return []
