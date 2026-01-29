"""
Local model provider implementation using Ollama.

Ollama allows running open-source models locally (Llama, Mistral, etc.)
See: https://ollama.ai/

To use:
1. Install Ollama: https://ollama.ai/download
2. Pull a model: ollama pull llama3
3. Start Ollama server (runs automatically on install)
4. Set LOCAL_MODEL_URL=http://localhost:11434 in .env
"""

from typing import Optional, AsyncIterator
import logging
import json

from app.ai_providers.base import (
    AIProvider,
    ModelInfo,
    AIProviderError,
    AIProviderUnavailableError,
    AIProviderInvalidResponseError
)

logger = logging.getLogger(__name__)


class LocalProvider(AIProvider):
    """
    Local model provider using Ollama.

    Supports any model available through Ollama (Llama, Mistral, CodeLlama, etc.)
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
        openai_api_key: Optional[str] = None  # For TTS fallback
    ):
        """
        Initialize local provider.

        Args:
            base_url: Ollama server URL
            model: Model name (must be pulled via `ollama pull <model>`)
            openai_api_key: Optional OpenAI key for TTS fallback
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.openai_api_key = openai_api_key
        self._client = None
        self._openai_provider = None

    @property
    def client(self):
        """Lazy initialization of HTTP client"""
        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(
                    timeout=60.0,
                    base_url=self.base_url
                )
            except ImportError:
                raise AIProviderError(
                    "httpx package not installed. Run: pip install httpx",
                    provider="local"
                )
        return self._client

    async def _check_health(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = await self.client.get("/")
            return response.status_code == 200
        except Exception:
            return False

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate completion using local Ollama model"""
        try:
            response = await self.client.post(
                "/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                }
            )

            if response.status_code != 200:
                error_text = response.text
                if "model" in error_text.lower() and "not found" in error_text.lower():
                    raise AIProviderError(
                        f"Model '{self.model}' not found. Run: ollama pull {self.model}",
                        provider="local"
                    )
                raise AIProviderError(
                    f"Ollama request failed: {error_text}",
                    provider="local"
                )

            data = response.json()
            content = data.get("message", {}).get("content", "")

            if not content:
                raise AIProviderInvalidResponseError(
                    "Ollama returned empty response",
                    provider="local"
                )

            return content.strip()

        except AIProviderError:
            raise
        except Exception as e:
            error_str = str(e)
            if "ConnectError" in type(e).__name__ or "connection" in error_str.lower():
                raise AIProviderUnavailableError(
                    f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?",
                    provider="local",
                    original_error=e
                )
            logger.error(f"Local model error: {e}")
            raise AIProviderError(
                f"Local model request failed: {error_str}",
                provider="local",
                original_error=e
            )

    async def generate_completion_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Generate streaming completion using local Ollama model"""
        try:
            async with self.client.stream(
                "POST",
                "/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": True,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Local model streaming error: {e}")
            raise AIProviderError(
                f"Local model streaming failed: {str(e)}",
                provider="local",
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

        Local models don't have TTS, so we fall back to OpenAI if available.
        """
        if self.openai_api_key:
            if self._openai_provider is None:
                from app.ai_providers.openai_provider import OpenAIProvider
                self._openai_provider = OpenAIProvider(
                    api_key=self.openai_api_key
                )

            return await self._openai_provider.generate_tts(text, voice, speed)

        raise NotImplementedError(
            "Local models do not support TTS. Configure OPENAI_API_KEY for TTS fallback."
        )

    def get_model_info(self) -> ModelInfo:
        """Get local model information"""
        return ModelInfo(
            provider="local",
            model_name=self.model,
            supports_tts=self.openai_api_key is not None,
            max_tokens=4096,
            context_window=8192  # Varies by model, using conservative default
        )

    def get_available_voices(self) -> list[str]:
        """Get available TTS voices (from OpenAI fallback)"""
        if self.openai_api_key:
            return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        return []

    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
