"""
OpenAI API provider implementation.

Supports GPT models for text generation and TTS for voice synthesis.
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


class OpenAIProvider(AIProvider):
    """OpenAI API provider implementation"""

    AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    # Model context windows
    CONTEXT_WINDOWS = {
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gpt-4-turbo": 128000,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 16385
    }

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        tts_model: str = "tts-1",
        default_voice: str = "nova"
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model to use for completions
            tts_model: Model to use for TTS
            default_voice: Default voice for TTS
        """
        if not api_key:
            raise AIProviderAuthError(
                "OpenAI API key is required",
                provider="openai"
            )

        self.api_key = api_key
        self.model = model
        self.tts_model = tts_model
        self.default_voice = default_voice
        self._client = None

    @property
    def client(self):
        """Lazy initialization of OpenAI client"""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise AIProviderError(
                    "openai package not installed. Run: pip install openai",
                    provider="openai"
                )
        return self._client

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate completion using OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            content = response.choices[0].message.content
            if not content:
                raise AIProviderInvalidResponseError(
                    "OpenAI returned empty response",
                    provider="openai"
                )

            return content.strip()

        except AIProviderError:
            raise
        except Exception as e:
            error_type = type(e).__name__

            if "RateLimitError" in error_type:
                raise AIProviderRateLimitError(
                    "OpenAI rate limit exceeded. Please try again later.",
                    provider="openai",
                    original_error=e
                )
            elif "AuthenticationError" in error_type:
                raise AIProviderAuthError(
                    "OpenAI authentication failed. Check your API key.",
                    provider="openai",
                    original_error=e
                )
            elif "APIConnectionError" in error_type or "APITimeoutError" in error_type:
                raise AIProviderUnavailableError(
                    "OpenAI API is unavailable. Please try again later.",
                    provider="openai",
                    original_error=e
                )
            else:
                logger.error(f"OpenAI error: {e}")
                raise AIProviderError(
                    f"OpenAI request failed: {str(e)}",
                    provider="openai",
                    original_error=e
                )

    async def generate_completion_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Generate streaming completion using OpenAI API"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise AIProviderError(
                f"OpenAI streaming failed: {str(e)}",
                provider="openai",
                original_error=e
            )

    async def generate_tts(
        self,
        text: str,
        voice: str = None,
        speed: float = 1.0
    ) -> bytes:
        """Generate TTS audio using OpenAI API"""
        voice = voice or self.default_voice

        if voice not in self.AVAILABLE_VOICES:
            logger.warning(f"Invalid voice '{voice}', using default '{self.default_voice}'")
            voice = self.default_voice

        # Clamp speed to valid range
        speed = max(0.25, min(4.0, speed))

        try:
            response = await self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text,
                speed=speed
            )

            return response.content

        except Exception as e:
            error_type = type(e).__name__

            if "RateLimitError" in error_type:
                raise AIProviderRateLimitError(
                    "OpenAI TTS rate limit exceeded",
                    provider="openai",
                    original_error=e
                )
            else:
                logger.error(f"OpenAI TTS error: {e}")
                raise AIProviderError(
                    f"OpenAI TTS failed: {str(e)}",
                    provider="openai",
                    original_error=e
                )

    def get_model_info(self) -> ModelInfo:
        """Get OpenAI model information"""
        return ModelInfo(
            provider="openai",
            model_name=self.model,
            supports_tts=True,
            max_tokens=4096,
            context_window=self.CONTEXT_WINDOWS.get(self.model, 8192)
        )

    def get_available_voices(self) -> list[str]:
        """Get available OpenAI TTS voices"""
        return self.AVAILABLE_VOICES.copy()
