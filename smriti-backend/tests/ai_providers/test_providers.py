"""
Unit tests for AI Provider abstraction layer.

Tests:
- Provider switching
- Mock provider behavior
- Factory functionality
- Error handling
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

# Import the modules we're testing
from app.ai_providers.base import (
    AIProvider,
    AIProviderError,
    AIProviderAuthError,
    AIProviderUnavailableError,
    ModelInfo
)
from app.ai_providers.mock_provider import MockAIProvider
from app.ai_providers.factory import (
    AIProviderFactory,
    get_ai_provider,
    reset_ai_provider,
    set_ai_provider
)


class TestMockProvider:
    """Test the mock provider for predictable behavior"""

    @pytest.fixture
    def mock_provider(self):
        return MockAIProvider()

    @pytest.mark.asyncio
    async def test_generate_completion_returns_string(self, mock_provider):
        """Test that generate_completion returns a non-empty string"""
        response = await mock_provider.generate_completion(
            system_prompt="You are a test assistant",
            user_prompt="Hello"
        )

        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_generate_completion_records_call(self, mock_provider):
        """Test that calls are recorded in history"""
        await mock_provider.generate_completion(
            system_prompt="test",
            user_prompt="test"
        )

        assert mock_provider.get_call_count() == 1
        assert mock_provider.call_history[0]["method"] == "generate_completion"

    @pytest.mark.asyncio
    async def test_generate_completion_with_custom_response(self):
        """Test that custom responses are returned"""
        custom_response = "This is my custom response"
        provider = MockAIProvider(responses={"completion": custom_response})

        response = await provider.generate_completion(
            system_prompt="test",
            user_prompt="test"
        )

        assert response == custom_response

    @pytest.mark.asyncio
    async def test_generate_tts_returns_bytes(self, mock_provider):
        """Test that generate_tts returns bytes"""
        audio = await mock_provider.generate_tts("Hello world", "nova")

        assert isinstance(audio, bytes)
        assert len(audio) > 0

    @pytest.mark.asyncio
    async def test_generate_tts_records_call(self, mock_provider):
        """Test that TTS calls are recorded"""
        await mock_provider.generate_tts("Hello", "nova", 1.0)

        assert mock_provider.get_call_count("generate_tts") == 1

    def test_get_model_info(self, mock_provider):
        """Test that model info is returned"""
        info = mock_provider.get_model_info()

        assert isinstance(info, ModelInfo)
        assert info.provider == "mock"
        assert info.supports_tts == True

    def test_get_available_voices(self, mock_provider):
        """Test that available voices are returned"""
        voices = mock_provider.get_available_voices()

        assert isinstance(voices, list)
        assert "nova" in voices

    @pytest.mark.asyncio
    async def test_should_fail_raises_error(self):
        """Test that should_fail configuration raises error"""
        provider = MockAIProvider(should_fail=True)

        with pytest.raises(AIProviderError):
            await provider.generate_completion("test", "test")

    def test_reset_history(self, mock_provider):
        """Test that reset_history clears call history"""
        mock_provider.call_history = [{"method": "test"}]
        mock_provider.reset_history()

        assert len(mock_provider.call_history) == 0

    @pytest.mark.asyncio
    async def test_streaming_completion(self, mock_provider):
        """Test streaming completion yields strings"""
        chunks = []
        async for chunk in mock_provider.generate_completion_stream(
            system_prompt="test",
            user_prompt="test"
        ):
            chunks.append(chunk)

        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0


class TestAIProviderFactory:
    """Test the provider factory"""

    def setup_method(self):
        """Reset factory state before each test"""
        reset_ai_provider()
        AIProviderFactory._providers = {}

    def test_register_provider(self):
        """Test registering a custom provider"""
        AIProviderFactory.register("custom", MockAIProvider)

        assert "custom" in AIProviderFactory.get_available_providers()

    def test_register_invalid_provider_raises_error(self):
        """Test that registering non-AIProvider raises error"""
        class NotAProvider:
            pass

        with pytest.raises(ValueError):
            AIProviderFactory.register("invalid", NotAProvider)

    def test_create_mock_provider(self):
        """Test creating a mock provider"""
        AIProviderFactory._ensure_registered()
        provider = AIProviderFactory.create("mock")

        assert isinstance(provider, MockAIProvider)

    def test_create_unknown_provider_raises_error(self):
        """Test that unknown provider name raises error"""
        AIProviderFactory._ensure_registered()

        with pytest.raises(AIProviderError) as exc_info:
            AIProviderFactory.create("unknown_provider")

        assert "unknown_provider" in str(exc_info.value)

    def test_get_available_providers(self):
        """Test listing available providers"""
        AIProviderFactory._ensure_registered()
        providers = AIProviderFactory.get_available_providers()

        assert "mock" in providers
        assert "openai" in providers
        assert "anthropic" in providers
        assert "local" in providers


class TestProviderSwitching:
    """Test switching between providers"""

    def setup_method(self):
        """Reset state before each test"""
        reset_ai_provider()
        AIProviderFactory._providers = {}

    @pytest.mark.asyncio
    async def test_switch_from_mock_to_mock(self):
        """Test switching between provider instances"""
        AIProviderFactory._ensure_registered()

        # Create first provider
        provider1 = AIProviderFactory.create("mock")
        response1 = await provider1.generate_completion("sys", "user")

        # Create second provider with different config
        provider2 = AIProviderFactory.create("mock", responses={"completion": "different"})
        response2 = await provider2.generate_completion("sys", "user")

        # They should be different instances
        assert provider1 is not provider2
        assert response2 == "different"

    def test_set_ai_provider_overrides_default(self):
        """Test that set_ai_provider overrides the cached provider"""
        custom_provider = MockAIProvider(responses={"completion": "custom"})
        set_ai_provider(custom_provider)

        provider = get_ai_provider()

        assert provider is custom_provider

    @pytest.mark.asyncio
    async def test_provider_switching_via_factory(self):
        """Test creating different provider types"""
        AIProviderFactory._ensure_registered()

        # All these should create valid providers (mock doesn't need API keys)
        mock = AIProviderFactory.create("mock")

        assert mock.get_model_info().provider == "mock"

    @pytest.mark.asyncio
    async def test_openai_provider_requires_api_key(self):
        """Test that OpenAI provider requires API key"""
        AIProviderFactory._ensure_registered()

        with pytest.raises(AIProviderAuthError):
            AIProviderFactory.create("openai", api_key=None)

    @pytest.mark.asyncio
    async def test_anthropic_provider_requires_api_key(self):
        """Test that Anthropic provider requires API key"""
        AIProviderFactory._ensure_registered()

        with pytest.raises(AIProviderAuthError):
            AIProviderFactory.create("anthropic", api_key=None)


class TestProviderValidation:
    """Test response validation"""

    def test_validate_response_empty_fails(self):
        """Test that empty response fails validation"""
        provider = MockAIProvider()

        assert provider.validate_response("") == False
        assert provider.validate_response("   ") == False
        assert provider.validate_response(None) == False

    def test_validate_response_normal_passes(self):
        """Test that normal response passes validation"""
        provider = MockAIProvider()

        assert provider.validate_response("This is a valid response.") == True

    def test_validate_response_red_flags_fail(self):
        """Test that responses with red flags fail"""
        provider = MockAIProvider()

        assert provider.validate_response("You should immediately seek help") == False
        assert provider.validate_response("I diagnose you with anxiety") == False


class TestErrorHandling:
    """Test error handling across providers"""

    @pytest.mark.asyncio
    async def test_provider_error_includes_provider_name(self):
        """Test that errors include provider name"""
        provider = MockAIProvider(should_fail=True)

        try:
            await provider.generate_completion("sys", "user")
        except AIProviderError as e:
            assert e.provider == "mock"
            assert "mock" in str(e)

    @pytest.mark.asyncio
    async def test_failure_rate_causes_random_failures(self):
        """Test that failure_rate causes some failures"""
        provider = MockAIProvider(failure_rate=1.0)  # 100% failure rate

        with pytest.raises(AIProviderError):
            await provider.generate_completion("sys", "user")


# Run tests with: pytest tests/ai_providers/test_providers.py -v
