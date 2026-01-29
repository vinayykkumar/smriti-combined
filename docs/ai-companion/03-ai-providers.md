# AI Reflection Companion - AI Provider Abstraction Design

## Document Info
- **Feature**: AI Reflection Companion
- **Phase**: AI Provider Abstraction Design
- **Created**: 2026-01-28
- **Status**: Complete

---

## 1. Design Goals

1. **Easy Switching**: Change AI provider via environment variable without code changes
2. **Consistent Interface**: All providers implement the same interface
3. **TTS Support**: Unified TTS interface across providers that support it
4. **Testability**: Easy to mock for testing
5. **Future-Proof**: Easy to add new providers (Google, Cohere, etc.)

---

## 2. Module Structure

```
smriti-backend/app/ai_providers/
├── __init__.py           # Package exports
├── base.py               # Abstract base class
├── openai_provider.py    # OpenAI implementation
├── anthropic_provider.py # Anthropic implementation
├── local_provider.py     # Ollama/local models
├── mock_provider.py      # Mock for testing
├── factory.py            # Provider factory
└── config.py             # Provider configuration
```

---

## 3. Abstract Base Class

```python
# app/ai_providers/base.py

from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator
from dataclasses import dataclass

@dataclass
class ModelInfo:
    """Information about the AI model"""
    provider: str
    model_name: str
    supports_tts: bool
    max_tokens: int
    context_window: int

@dataclass
class CompletionRequest:
    """Request for text completion"""
    system_prompt: str
    user_prompt: str
    max_tokens: int = 500
    temperature: float = 0.7
    stop_sequences: Optional[list[str]] = None

@dataclass
class TTSRequest:
    """Request for text-to-speech"""
    text: str
    voice: str
    speed: float = 1.0

class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    All AI providers must implement this interface to ensure
    consistent behavior across the application.
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

        Yields:
            Text chunks as they are generated
        """
        pass

    @abstractmethod
    async def generate_tts(
        self,
        text: str,
        voice: str,
        speed: float = 1.0
    ) -> bytes:
        """
        Generate text-to-speech audio.

        Args:
            text: Text to convert to speech
            voice: Voice identifier
            speed: Playback speed multiplier

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

class AIProviderError(Exception):
    """Base exception for AI provider errors"""

    def __init__(self, message: str, provider: str, original_error: Optional[Exception] = None):
        self.message = message
        self.provider = provider
        self.original_error = original_error
        super().__init__(self.message)

class AIProviderRateLimitError(AIProviderError):
    """Rate limit exceeded"""
    pass

class AIProviderAuthError(AIProviderError):
    """Authentication failed"""
    pass

class AIProviderUnavailableError(AIProviderError):
    """Provider service unavailable"""
    pass
```

---

## 4. OpenAI Provider Implementation

```python
# app/ai_providers/openai_provider.py

from typing import Optional, AsyncIterator
import openai
from openai import AsyncOpenAI

from app.ai_providers.base import (
    AIProvider,
    ModelInfo,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderAuthError,
    AIProviderUnavailableError
)
from app.config.settings import settings

class OpenAIProvider(AIProvider):
    """OpenAI API provider implementation"""

    AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        tts_model: Optional[str] = None
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.tts_model = tts_model or settings.OPENAI_TTS_MODEL

        if not self.api_key:
            raise AIProviderAuthError(
                "OpenAI API key not configured",
                provider="openai"
            )

        self.client = AsyncOpenAI(api_key=self.api_key)

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
            return response.choices[0].message.content.strip()

        except openai.RateLimitError as e:
            raise AIProviderRateLimitError(
                "OpenAI rate limit exceeded",
                provider="openai",
                original_error=e
            )
        except openai.AuthenticationError as e:
            raise AIProviderAuthError(
                "OpenAI authentication failed",
                provider="openai",
                original_error=e
            )
        except openai.APIConnectionError as e:
            raise AIProviderUnavailableError(
                "OpenAI API unavailable",
                provider="openai",
                original_error=e
            )
        except Exception as e:
            raise AIProviderError(
                f"OpenAI error: {str(e)}",
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
            raise AIProviderError(
                f"OpenAI streaming error: {str(e)}",
                provider="openai",
                original_error=e
            )

    async def generate_tts(
        self,
        text: str,
        voice: str,
        speed: float = 1.0
    ) -> bytes:
        """Generate TTS audio using OpenAI API"""
        if voice not in self.AVAILABLE_VOICES:
            voice = "nova"  # Default to calm voice

        try:
            response = await self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text,
                speed=speed
            )
            return response.content

        except openai.RateLimitError as e:
            raise AIProviderRateLimitError(
                "OpenAI TTS rate limit exceeded",
                provider="openai",
                original_error=e
            )
        except Exception as e:
            raise AIProviderError(
                f"OpenAI TTS error: {str(e)}",
                provider="openai",
                original_error=e
            )

    def get_model_info(self) -> ModelInfo:
        """Get OpenAI model information"""
        # Context windows vary by model
        context_windows = {
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385
        }

        return ModelInfo(
            provider="openai",
            model_name=self.model,
            supports_tts=True,
            max_tokens=4096,
            context_window=context_windows.get(self.model, 8192)
        )

    def get_available_voices(self) -> list[str]:
        """Get available OpenAI TTS voices"""
        return self.AVAILABLE_VOICES.copy()
```

---

## 5. Anthropic Provider Implementation

```python
# app/ai_providers/anthropic_provider.py

from typing import Optional, AsyncIterator
import anthropic
from anthropic import AsyncAnthropic

from app.ai_providers.base import (
    AIProvider,
    ModelInfo,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderAuthError,
    AIProviderUnavailableError
)
from app.config.settings import settings

class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider implementation"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL

        if not self.api_key:
            raise AIProviderAuthError(
                "Anthropic API key not configured",
                provider="anthropic"
            )

        self.client = AsyncAnthropic(api_key=self.api_key)

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
            return response.content[0].text.strip()

        except anthropic.RateLimitError as e:
            raise AIProviderRateLimitError(
                "Anthropic rate limit exceeded",
                provider="anthropic",
                original_error=e
            )
        except anthropic.AuthenticationError as e:
            raise AIProviderAuthError(
                "Anthropic authentication failed",
                provider="anthropic",
                original_error=e
            )
        except anthropic.APIConnectionError as e:
            raise AIProviderUnavailableError(
                "Anthropic API unavailable",
                provider="anthropic",
                original_error=e
            )
        except Exception as e:
            raise AIProviderError(
                f"Anthropic error: {str(e)}",
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
            raise AIProviderError(
                f"Anthropic streaming error: {str(e)}",
                provider="anthropic",
                original_error=e
            )

    async def generate_tts(
        self,
        text: str,
        voice: str,
        speed: float = 1.0
    ) -> bytes:
        """
        Anthropic doesn't have native TTS.
        Falls back to OpenAI TTS or raises NotImplementedError.
        """
        # Option 1: Raise error
        # raise NotImplementedError("Anthropic does not support TTS")

        # Option 2: Fall back to OpenAI for TTS
        from app.ai_providers.openai_provider import OpenAIProvider
        if settings.OPENAI_API_KEY:
            openai_provider = OpenAIProvider()
            return await openai_provider.generate_tts(text, voice, speed)

        raise NotImplementedError(
            "TTS not available: Anthropic doesn't support TTS and OpenAI fallback not configured"
        )

    def get_model_info(self) -> ModelInfo:
        """Get Anthropic model information"""
        context_windows = {
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-3-5-sonnet-20241022": 200000
        }

        return ModelInfo(
            provider="anthropic",
            model_name=self.model,
            supports_tts=False,  # Anthropic doesn't have TTS
            max_tokens=4096,
            context_window=context_windows.get(self.model, 200000)
        )

    def get_available_voices(self) -> list[str]:
        """Anthropic doesn't have TTS voices"""
        return []
```

---

## 6. Local Model Provider (Ollama)

```python
# app/ai_providers/local_provider.py

from typing import Optional, AsyncIterator
import httpx

from app.ai_providers.base import (
    AIProvider,
    ModelInfo,
    AIProviderError,
    AIProviderUnavailableError
)
from app.config.settings import settings

class LocalProvider(AIProvider):
    """
    Local model provider using Ollama.

    Ollama must be running locally with the specified model pulled.
    Example: ollama pull llama3
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.base_url = base_url or settings.LOCAL_MODEL_URL
        self.model = model or settings.LOCAL_MODEL_NAME
        self.client = httpx.AsyncClient(timeout=60.0)

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
                f"{self.base_url}/api/chat",
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
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"].strip()

        except httpx.ConnectError as e:
            raise AIProviderUnavailableError(
                f"Local model unavailable at {self.base_url}",
                provider="local",
                original_error=e
            )
        except Exception as e:
            raise AIProviderError(
                f"Local model error: {str(e)}",
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
                f"{self.base_url}/api/chat",
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
                        import json
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]

        except Exception as e:
            raise AIProviderError(
                f"Local model streaming error: {str(e)}",
                provider="local",
                original_error=e
            )

    async def generate_tts(
        self,
        text: str,
        voice: str,
        speed: float = 1.0
    ) -> bytes:
        """
        Local TTS using system TTS or external service.

        For production, consider using:
        - Coqui TTS (open source)
        - Piper (fast local TTS)
        - System TTS (espeak, say command)
        """
        # Option 1: Fall back to OpenAI
        from app.ai_providers.openai_provider import OpenAIProvider
        if settings.OPENAI_API_KEY:
            openai_provider = OpenAIProvider()
            return await openai_provider.generate_tts(text, voice, speed)

        raise NotImplementedError(
            "Local TTS not implemented. Configure OpenAI API key for TTS fallback."
        )

    def get_model_info(self) -> ModelInfo:
        """Get local model information"""
        return ModelInfo(
            provider="local",
            model_name=self.model,
            supports_tts=False,
            max_tokens=4096,
            context_window=8192  # Varies by model
        )

    def get_available_voices(self) -> list[str]:
        """Local models don't have TTS voices"""
        return []

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
```

---

## 7. Mock Provider for Testing

```python
# app/ai_providers/mock_provider.py

from typing import AsyncIterator
import asyncio

from app.ai_providers.base import AIProvider, ModelInfo

class MockAIProvider(AIProvider):
    """
    Mock AI provider for testing.

    Returns predictable responses for testing purposes.
    """

    def __init__(self, responses: dict = None):
        self.responses = responses or {}
        self.call_history = []

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Return mock completion"""
        self.call_history.append({
            "method": "generate_completion",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        })

        # Return custom response if provided
        if "completion" in self.responses:
            return self.responses["completion"]

        # Default mock response
        return "This is a thoughtful reflection prompt for your contemplative practice. Consider what brings you peace in this moment."

    async def generate_completion_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Return mock streaming completion"""
        response = await self.generate_completion(
            system_prompt, user_prompt, max_tokens, temperature
        )
        # Simulate streaming by yielding words
        for word in response.split():
            yield word + " "
            await asyncio.sleep(0.05)  # Simulate delay

    async def generate_tts(
        self,
        text: str,
        voice: str,
        speed: float = 1.0
    ) -> bytes:
        """Return mock TTS audio"""
        self.call_history.append({
            "method": "generate_tts",
            "text": text,
            "voice": voice
        })

        # Return custom response if provided
        if "tts" in self.responses:
            return self.responses["tts"]

        # Return minimal valid MP3 header for testing
        # This is a tiny valid MP3 file (silence)
        return b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    def get_model_info(self) -> ModelInfo:
        """Return mock model info"""
        return ModelInfo(
            provider="mock",
            model_name="mock-model",
            supports_tts=True,
            max_tokens=4096,
            context_window=8192
        )

    def get_available_voices(self) -> list[str]:
        """Return mock voices"""
        return ["mock-voice-1", "mock-voice-2"]

    def reset_history(self):
        """Reset call history for testing"""
        self.call_history = []
```

---

## 8. Provider Factory

```python
# app/ai_providers/factory.py

from typing import Optional
from functools import lru_cache

from app.ai_providers.base import AIProvider, AIProviderError
from app.ai_providers.openai_provider import OpenAIProvider
from app.ai_providers.anthropic_provider import AnthropicProvider
from app.ai_providers.local_provider import LocalProvider
from app.ai_providers.mock_provider import MockAIProvider
from app.config.settings import settings

class AIProviderFactory:
    """
    Factory for creating AI provider instances.

    Supports:
    - openai: OpenAI GPT models with TTS
    - anthropic: Anthropic Claude models
    - local: Local Ollama models
    - mock: Mock provider for testing
    """

    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "local": LocalProvider,
        "mock": MockAIProvider
    }

    @classmethod
    def create(
        cls,
        provider_name: Optional[str] = None,
        **kwargs
    ) -> AIProvider:
        """
        Create an AI provider instance.

        Args:
            provider_name: Provider name (openai, anthropic, local, mock)
            **kwargs: Additional arguments passed to provider constructor

        Returns:
            Configured AIProvider instance

        Raises:
            AIProviderError: If provider is not supported
        """
        name = provider_name or settings.AI_PROVIDER

        if name not in cls._providers:
            raise AIProviderError(
                f"Unknown AI provider: {name}. Supported: {list(cls._providers.keys())}",
                provider=name
            )

        provider_class = cls._providers[name]
        return provider_class(**kwargs)

    @classmethod
    def register(cls, name: str, provider_class: type):
        """
        Register a new provider type.

        Args:
            name: Provider identifier
            provider_class: Provider class (must inherit from AIProvider)
        """
        if not issubclass(provider_class, AIProvider):
            raise ValueError(f"{provider_class} must inherit from AIProvider")
        cls._providers[name] = provider_class

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names"""
        return list(cls._providers.keys())


# Cached provider instance for dependency injection
@lru_cache()
def get_ai_provider() -> AIProvider:
    """
    Get a cached AI provider instance.

    This is used for FastAPI dependency injection.
    The provider is cached to reuse connections.
    """
    return AIProviderFactory.create()


def get_ai_provider_uncached() -> AIProvider:
    """
    Get a new AI provider instance (not cached).

    Use this when you need a fresh instance.
    """
    return AIProviderFactory.create()
```

---

## 9. Configuration

```python
# app/ai_providers/config.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""
    name: str
    display_name: str
    supports_tts: bool
    default_model: str
    available_models: list[str]
    tts_voices: list[str]
    requires_api_key: bool

# Provider configurations
PROVIDER_CONFIGS = {
    "openai": ProviderConfig(
        name="openai",
        display_name="OpenAI",
        supports_tts=True,
        default_model="gpt-4o-mini",
        available_models=[
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ],
        tts_voices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        requires_api_key=True
    ),
    "anthropic": ProviderConfig(
        name="anthropic",
        display_name="Anthropic",
        supports_tts=False,
        default_model="claude-3-haiku-20240307",
        available_models=[
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        tts_voices=[],
        requires_api_key=True
    ),
    "local": ProviderConfig(
        name="local",
        display_name="Local (Ollama)",
        supports_tts=False,
        default_model="llama3",
        available_models=["llama3", "llama2", "mistral", "codellama"],
        tts_voices=[],
        requires_api_key=False
    )
}

def get_provider_config(provider_name: str) -> Optional[ProviderConfig]:
    """Get configuration for a provider"""
    return PROVIDER_CONFIGS.get(provider_name)
```

---

## 10. Package Exports

```python
# app/ai_providers/__init__.py

from app.ai_providers.base import (
    AIProvider,
    ModelInfo,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderAuthError,
    AIProviderUnavailableError
)
from app.ai_providers.factory import (
    AIProviderFactory,
    get_ai_provider,
    get_ai_provider_uncached
)
from app.ai_providers.config import (
    ProviderConfig,
    PROVIDER_CONFIGS,
    get_provider_config
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
    "get_ai_provider",
    "get_ai_provider_uncached",
    # Config
    "ProviderConfig",
    "PROVIDER_CONFIGS",
    "get_provider_config"
]
```

---

## 11. Usage Examples

### Basic Usage

```python
from app.ai_providers import get_ai_provider

# Get default provider (from settings)
provider = get_ai_provider()

# Generate completion
response = await provider.generate_completion(
    system_prompt="You are a thoughtful meditation guide.",
    user_prompt="Give me a reflection prompt about gratitude.",
    max_tokens=200
)
print(response)

# Generate TTS
audio = await provider.generate_tts(
    text="Welcome to this moment of stillness.",
    voice="nova"
)
# Save or stream audio
```

### Switching Providers

```python
from app.ai_providers import AIProviderFactory

# Use specific provider
openai = AIProviderFactory.create("openai")
anthropic = AIProviderFactory.create("anthropic")
local = AIProviderFactory.create("local")

# Or set in environment
# AI_PROVIDER=anthropic
```

### Testing

```python
from app.ai_providers import AIProviderFactory
from app.ai_providers.mock_provider import MockAIProvider

# Create mock with custom responses
mock = MockAIProvider(responses={
    "completion": "Custom test response",
    "tts": b"custom audio bytes"
})

# Use in tests
response = await mock.generate_completion(
    system_prompt="test",
    user_prompt="test"
)
assert response == "Custom test response"
assert len(mock.call_history) == 1
```

---

## 12. Environment Variables

```bash
# .env file

# AI Provider Selection
AI_PROVIDER=openai  # openai | anthropic | local | mock

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=nova

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Local Model Configuration (optional)
LOCAL_MODEL_URL=http://localhost:11434
LOCAL_MODEL_NAME=llama3
```

---

## 13. Testing Strategy

### Unit Tests
- Test each provider independently
- Test factory creates correct provider type
- Test error handling for each provider
- Test mock provider for predictable behavior

### Integration Tests
- Test with real API (use test accounts)
- Test TTS audio generation
- Test streaming responses
- Test fallback behavior (Anthropic TTS -> OpenAI)

### Mock for CI/CD
```python
# In conftest.py
import pytest
from app.ai_providers.mock_provider import MockAIProvider

@pytest.fixture
def mock_ai_provider():
    return MockAIProvider()

@pytest.fixture(autouse=True)
def override_ai_provider(mock_ai_provider, monkeypatch):
    """Use mock provider in all tests"""
    monkeypatch.setattr(
        "app.ai_providers.factory.get_ai_provider",
        lambda: mock_ai_provider
    )
```
