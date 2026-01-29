"""
Mock AI provider for testing.

Returns predictable responses without making actual API calls.
Useful for:
- Unit testing
- UI development
- Offline development
- CI/CD pipelines
"""

from typing import Optional, AsyncIterator
import asyncio
import random

from app.ai_providers.base import AIProvider, ModelInfo


class MockAIProvider(AIProvider):
    """
    Mock AI provider for testing.

    Can be configured with custom responses or uses sensible defaults.
    """

    # Default responses for different prompt types
    DEFAULT_REFLECTION_PROMPTS = [
        "What is asking for your attention in this moment that you have not yet acknowledged?",
        "If you were to be completely honest with yourself right now, what truth would you speak?",
        "Consider the quality of your attention today. Where does it naturally want to rest?",
        "What small thing are you grateful for that you usually overlook?",
        "What would it mean to fully accept where you are, exactly as things are?"
    ]

    DEFAULT_CONTEMPLATIVE_QUESTIONS = [
        "Who are you when you are not playing any role?",
        "What would remain if you let go of the need to be certain?",
        "What truth have you been avoiding, and what would change if you acknowledged it?",
        "If this moment were complete in itself, what would you notice?"
    ]

    DEFAULT_MEDITATION_GUIDANCE = {
        "opening": "Welcome to this moment of stillness. Allow your body to settle into a comfortable position. There is nowhere else you need to be right now.",
        "settling": "Begin to notice your breath, without trying to change it. Simply observe the natural rhythm of inhaling and exhaling.",
        "intervals": [
            "Gently return your attention to your breath. If your mind has wandered, that's perfectly natural. Simply begin again.",
            "Notice any areas of tension in your body. With each exhale, invite those areas to soften.",
            "You're doing beautifully. Continue resting in this present moment."
        ],
        "closing": "Begin to deepen your breath slightly. Slowly bring your awareness back to the room around you. When you're ready, gently open your eyes."
    }

    AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(
        self,
        responses: Optional[dict] = None,
        delay: float = 0.1,
        should_fail: bool = False,
        failure_rate: float = 0.0
    ):
        """
        Initialize mock provider.

        Args:
            responses: Custom responses dict (keys: "completion", "tts", "stream")
            delay: Simulated delay in seconds
            should_fail: If True, always raise an error
            failure_rate: Probability of random failure (0.0 to 1.0)
        """
        self.responses = responses or {}
        self.delay = delay
        self.should_fail = should_fail
        self.failure_rate = failure_rate
        self.call_history: list[dict] = []

    def _maybe_fail(self):
        """Raise error if configured to fail"""
        if self.should_fail:
            from app.ai_providers.base import AIProviderError
            raise AIProviderError("Mock provider configured to fail", provider="mock")

        if self.failure_rate > 0 and random.random() < self.failure_rate:
            from app.ai_providers.base import AIProviderUnavailableError
            raise AIProviderUnavailableError("Random mock failure", provider="mock")

    def _record_call(self, method: str, **kwargs):
        """Record call for testing assertions"""
        self.call_history.append({
            "method": method,
            **kwargs
        })

    def _detect_prompt_type(self, user_prompt: str) -> str:
        """Detect the type of prompt from content"""
        prompt_lower = user_prompt.lower()

        if "meditation" in prompt_lower or "guidance" in prompt_lower:
            return "meditation"
        elif "question" in prompt_lower or "contemplate" in prompt_lower:
            return "question"
        else:
            return "reflection"

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Return mock completion"""
        self._record_call(
            "generate_completion",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

        self._maybe_fail()
        await asyncio.sleep(self.delay)

        # Return custom response if provided
        if "completion" in self.responses:
            return self.responses["completion"]

        # Detect prompt type and return appropriate response
        prompt_type = self._detect_prompt_type(user_prompt)

        if prompt_type == "meditation":
            import json
            return json.dumps(self.DEFAULT_MEDITATION_GUIDANCE)
        elif prompt_type == "question":
            question = random.choice(self.DEFAULT_CONTEMPLATIVE_QUESTIONS)
            return f'{{"question": "{question}", "follow_ups": ["What does this reveal?", "How does this connect to your deepest values?"]}}'
        else:
            return random.choice(self.DEFAULT_REFLECTION_PROMPTS)

    async def generate_completion_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Return mock streaming completion"""
        self._record_call(
            "generate_completion_stream",
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        self._maybe_fail()

        response = await self.generate_completion(
            system_prompt, user_prompt, max_tokens, temperature
        )

        # Simulate streaming by yielding words
        words = response.split()
        for word in words:
            yield word + " "
            await asyncio.sleep(self.delay / len(words))

    async def generate_tts(
        self,
        text: str,
        voice: str = "nova",
        speed: float = 1.0
    ) -> bytes:
        """Return mock TTS audio"""
        self._record_call(
            "generate_tts",
            text=text,
            voice=voice,
            speed=speed
        )

        self._maybe_fail()
        await asyncio.sleep(self.delay)

        # Return custom response if provided
        if "tts" in self.responses:
            return self.responses["tts"]

        # Return minimal valid MP3 header (silence)
        # This is a tiny valid MP3 frame for testing
        return bytes([
            0xFF, 0xFB, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])

    def get_model_info(self) -> ModelInfo:
        """Return mock model info"""
        return ModelInfo(
            provider="mock",
            model_name="mock-model-v1",
            supports_tts=True,
            max_tokens=4096,
            context_window=8192
        )

    def get_available_voices(self) -> list[str]:
        """Return available mock voices"""
        return self.AVAILABLE_VOICES.copy()

    def reset_history(self):
        """Reset call history for testing"""
        self.call_history = []

    def get_call_count(self, method: Optional[str] = None) -> int:
        """Get number of calls, optionally filtered by method"""
        if method:
            return len([c for c in self.call_history if c["method"] == method])
        return len(self.call_history)
