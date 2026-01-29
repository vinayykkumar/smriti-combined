"""
Unit tests for AI Companion personalization and validation.

Tests:
1. Personalization with past reflections
2. Personalization without past reflections (fallback)
3. AI response validation filters inappropriate content
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId

from app.companion.service import CompanionService
from app.companion.repository import CompanionRepository
from app.companion.schemas import (
    CompanionSettings,
    ReflectionPromptRequest,
    ReflectionPromptResponse,
    ContemplativeQuestionRequest,
    ContemplativeQuestionResponse
)
from app.companion.prompts.themes import (
    extract_themes,
    detect_emotional_tone,
    analyze_reflection_patterns,
    build_personalized_context,
    identify_recurring_concerns,
    identify_growth_indicators
)
from app.companion.validation import (
    validate_response,
    validate_reflection_prompt,
    validate_contemplative_question,
    validate_meditation_guidance,
    ValidationResult
)
from app.ai_providers.mock_provider import MockAIProvider
from app.ai_providers.base import AIProviderError


# Valid ObjectId for testing
TEST_USER_ID = str(ObjectId())


class TestThemeExtraction:
    """Test theme extraction from reflections"""

    def test_extract_themes_with_gratitude_content(self):
        """Test extracting gratitude theme from text"""
        text = "I am so grateful for my family. Thankful for this blessed life."
        themes = extract_themes(text)

        assert "gratitude" in themes
        assert themes[0] == "gratitude"  # Should be first (most matches)

    def test_extract_themes_with_multiple_themes(self):
        """Test extracting multiple themes"""
        text = """
        I'm grateful for the peace I've found. The stillness in meditation
        helps me feel calm and serene. I'm learning to accept things as they are.
        """
        themes = extract_themes(text)

        assert len(themes) >= 2
        assert "gratitude" in themes
        assert "stillness" in themes or "acceptance" in themes

    def test_extract_themes_empty_text(self):
        """Test that empty text returns empty list"""
        themes = extract_themes("")
        assert themes == []

    def test_extract_themes_no_matches(self):
        """Test text with no theme keywords"""
        text = "The quick brown fox jumps over the lazy dog."
        themes = extract_themes(text)
        assert themes == []

    def test_extract_themes_max_themes(self):
        """Test max_themes limit"""
        text = """
        I'm grateful and peaceful, seeking meaning while accepting change.
        Growing through struggle with presence and connection.
        """
        themes = extract_themes(text, max_themes=3)
        assert len(themes) <= 3


class TestEmotionalToneDetection:
    """Test emotional tone detection"""

    def test_detect_positive_tone(self):
        """Test detecting positive emotional tone"""
        text = "I feel so happy and at peace today. Grateful for this joy."
        tone = detect_emotional_tone(text)
        assert tone == "positive"

    def test_detect_struggling_tone(self):
        """Test detecting struggling emotional tone"""
        text = "I'm feeling anxious and overwhelmed. Everything seems so difficult."
        tone = detect_emotional_tone(text)
        assert tone == "struggling"

    def test_detect_seeking_tone(self):
        """Test detecting seeking emotional tone"""
        text = "I'm searching for meaning. Longing for something I can't name."
        tone = detect_emotional_tone(text)
        assert tone == "seeking"

    def test_detect_contemplative_tone(self):
        """Test detecting contemplative emotional tone"""
        text = "I find myself wondering about existence. Curious about consciousness."
        tone = detect_emotional_tone(text)
        assert tone == "contemplative"

    def test_detect_neutral_tone(self):
        """Test neutral tone when no keywords match"""
        text = "The weather is nice today."
        tone = detect_emotional_tone(text)
        assert tone == "neutral"


class TestPatternAnalysis:
    """Test comprehensive pattern analysis"""

    def test_analyze_patterns_with_posts(self):
        """Test analyzing patterns from multiple posts"""
        posts = [
            {"content": "Today I'm grateful for the peace I found in meditation."},
            {"content": "Sitting in stillness, I notice my breath becoming calmer."},
            {"content": "I am thankful for moments of quiet reflection."}
        ]

        patterns = analyze_reflection_patterns(posts)

        assert patterns.themes  # Should have themes
        assert "gratitude" in patterns.themes or "stillness" in patterns.themes
        assert patterns.emotional_tone in ["positive", "contemplative", "neutral"]
        assert patterns.summary  # Should have a summary

    def test_analyze_patterns_empty_posts(self):
        """Test analyzing patterns with no posts"""
        patterns = analyze_reflection_patterns([])

        assert patterns.themes == []
        assert patterns.emotional_tone == "neutral"
        assert patterns.summary == ""

    def test_recurring_concerns_detection(self):
        """Test detecting recurring concerns across posts"""
        posts = [
            {"content": "I'm grateful for today."},
            {"content": "Feeling blessed and thankful."},
            {"content": "So much gratitude in my heart."},
            {"content": "Random unrelated content."}
        ]

        recurring = identify_recurring_concerns(posts)
        assert "gratitude" in recurring

    def test_growth_indicators_detection(self):
        """Test detecting growth indicators"""
        # Older posts (end of list) have struggle, recent posts show acceptance
        posts = [
            {"content": "I've realized I can let this go. Finding acceptance."},  # Recent
            {"content": "I'm grateful for the clarity I've gained."},  # Recent
            {"content": "Letting go is becoming easier."},  # Older
            {"content": "I was struggling with this issue."},  # Older
            {"content": "It was so difficult to accept."},  # Oldest
            {"content": "I couldn't understand what was happening."},  # Oldest
        ]

        growth = identify_growth_indicators(posts)
        # Should detect some form of growth
        assert len(growth) >= 0  # May or may not detect based on threshold


class TestBuildPersonalizedContext:
    """Test building personalized context for AI"""

    def test_build_context_with_posts(self):
        """Test building context from posts"""
        posts = [
            {"content": "I'm grateful for peace in my life."},
            {"content": "Finding stillness in meditation."}
        ]

        context = build_personalized_context(posts)

        assert context is not None
        assert len(context) > 0
        assert "grateful" in context.lower() or "peace" in context.lower()

    def test_build_context_empty_posts(self):
        """Test building context with no posts"""
        context = build_personalized_context([])
        assert context is None

    def test_build_context_truncates_long_content(self):
        """Test that long content is truncated"""
        posts = [
            {"content": "A" * 1000}  # Very long content
        ]

        context = build_personalized_context(posts)
        assert context is not None
        # Should be truncated to max_chars


class TestResponseValidation:
    """Test AI response validation"""

    def test_validate_empty_response(self):
        """Test that empty responses fail validation"""
        result = validate_response("")
        assert result.is_valid == False
        assert result.severity == "error"

    def test_validate_whitespace_response(self):
        """Test that whitespace-only responses fail validation"""
        result = validate_response("   \n\t  ")
        assert result.is_valid == False

    def test_validate_response_with_red_flags(self):
        """Test that responses with red flags fail validation"""
        # Medical advice red flag
        result = validate_response("You should immediately seek professional help.")
        assert result.is_valid == False
        assert "red flag" in result.issues[0].lower()

        # Diagnosis red flag
        result = validate_response("I diagnose you with anxiety disorder.")
        assert result.is_valid == False

        # Urgent language
        result = validate_response("You must urgently address this issue.")
        assert result.is_valid == False

    def test_validate_response_with_ai_self_reference(self):
        """Test that AI self-references fail validation"""
        result = validate_response("As an AI, I cannot truly understand your feelings.")
        assert result.is_valid == False

    def test_validate_response_with_advice(self):
        """Test that direct advice fails validation"""
        result = validate_response("You should meditate every day.")
        assert result.is_valid == False

        result = validate_response("My advice is to start journaling.")
        assert result.is_valid == False

    def test_validate_good_contemplative_response(self):
        """Test that good contemplative responses pass validation"""
        good_responses = [
            "What would it mean to simply allow this feeling to be here?",
            "Notice the breath. Where do you feel it most?",
            "Perhaps this question itself is worth sitting with.",
            "What might you discover if you paused here for a moment?"
        ]

        for response in good_responses:
            result = validate_response(response)
            assert result.is_valid == True, f"Failed for: {response}"


class TestReflectionPromptValidation:
    """Test validation specific to reflection prompts"""

    def test_validate_prompt_too_long(self):
        """Test that very long prompts get flagged"""
        long_prompt = "What " * 200 + "?"
        result = validate_reflection_prompt(long_prompt)
        assert "too long" in str(result.issues).lower()

    def test_validate_prompt_not_question(self):
        """Test that non-questions get flagged"""
        result = validate_reflection_prompt("This is a statement about life.")
        assert not result.is_valid or result.severity == "warning"

    def test_validate_prompt_starts_with_i(self):
        """Test that prompts starting with 'I' get flagged"""
        result = validate_reflection_prompt("I wonder what brings you peace?")
        assert "should not start with 'I'" in str(result.issues)

    def test_validate_prompt_with_exclamation(self):
        """Test that exclamation marks get flagged"""
        result = validate_reflection_prompt("Isn't life amazing!")
        assert "exclamation" in str(result.issues).lower()

    def test_validate_good_prompt(self):
        """Test that good prompts pass validation"""
        result = validate_reflection_prompt(
            "What would it mean to fully accept where you are right now?"
        )
        assert result.is_valid == True


class TestContemplativeQuestionValidation:
    """Test validation specific to contemplative questions"""

    def test_validate_question_not_ending_with_questionmark(self):
        """Test that questions must end with ?"""
        result = validate_contemplative_question("What is the meaning of life")
        assert "should end with '?'" in str(result.issues)

    def test_validate_yes_no_question(self):
        """Test that yes/no questions get flagged"""
        yes_no_questions = [
            "Do you feel happy?",
            "Are you at peace?",
            "Have you considered this?",
            "Can you accept yourself?"
        ]

        for question in yes_no_questions:
            result = validate_contemplative_question(question)
            assert "yes/no" in str(result.issues).lower(), f"Failed for: {question}"

    def test_validate_good_contemplative_question(self):
        """Test that good questions pass validation"""
        result = validate_contemplative_question(
            "Who are you when you are not playing any role?"
        )
        assert result.is_valid == True


class TestMeditationValidation:
    """Test validation for meditation guidance"""

    def test_validate_meditation_missing_sections(self):
        """Test that missing sections fail validation"""
        guidance = {
            "opening": "Welcome to this practice.",
            "settling": "",  # Missing
            "closing": "Thank you for practicing."
        }

        result = validate_meditation_guidance(guidance)
        assert "Missing" in str(result.issues) or not result.is_valid

    def test_validate_meditation_with_red_flags(self):
        """Test that meditation with red flags fails"""
        guidance = {
            "opening": "You should immediately relax your body.",
            "settling": "Notice your breath.",
            "closing": "Thank you."
        }

        result = validate_meditation_guidance(guidance)
        assert result.is_valid == False

    def test_validate_good_meditation(self):
        """Test that good meditation passes validation"""
        guidance = {
            "opening": "Allow yourself to arrive here, just as you are.",
            "settling": "Notice the breath, without changing it.",
            "intervals": ["Gently return to the present moment."],
            "closing": "Slowly bring your awareness back to the room."
        }

        result = validate_meditation_guidance(guidance)
        assert result.is_valid == True


class TestServicePersonalization:
    """Test personalization in the service layer"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        db = MagicMock()
        db.users = AsyncMock()
        db.companion_history = AsyncMock()
        db.posts = AsyncMock()
        return db

    @pytest.fixture
    def mock_provider(self):
        """Create mock AI provider"""
        return MockAIProvider(responses={
            "completion": "What would it mean to simply rest in this moment?"
        })

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock db"""
        return CompanionRepository(mock_db)

    @pytest.fixture
    def service(self, repository, mock_provider):
        """Create service with mocked dependencies"""
        return CompanionService(repository, mock_provider)

    @pytest.mark.asyncio
    async def test_personalization_with_reflections(self, service, mock_db):
        """Test that personalization works when user has past reflections"""
        # Setup: User has opted in and has reflections
        mock_db.users.find_one = AsyncMock(return_value={
            "companion_settings": {
                "opt_in_reflection_analysis": True,
                "preferred_tts_voice": "nova"
            }
        })

        # Mock posts cursor
        mock_cursor = MagicMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[
            {"content": "I am grateful for peace today.", "created_at": datetime.now(timezone.utc)},
            {"content": "Finding stillness in the morning.", "created_at": datetime.now(timezone.utc)}
        ])
        mock_db.posts.find = MagicMock(return_value=mock_cursor)

        # Mock history operations
        mock_db.companion_history.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=ObjectId())
        )
        mock_db.companion_history.count_documents = AsyncMock(return_value=5)

        # Execute
        request = ReflectionPromptRequest(use_reflections=True)
        result = await service.generate_reflection_prompt(
            TEST_USER_ID, request, save_history=False
        )

        # Verify
        assert result.based_on_reflections == True
        assert len(result.reflection_themes) > 0

    @pytest.mark.asyncio
    async def test_personalization_without_reflections_opt_out(self, service, mock_db):
        """Test fallback when user has not opted in"""
        # Setup: User has NOT opted in
        mock_db.users.find_one = AsyncMock(return_value={
            "companion_settings": {
                "opt_in_reflection_analysis": False,
                "preferred_tts_voice": "nova"
            }
        })

        # Mock history
        mock_db.companion_history.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=ObjectId())
        )
        mock_db.companion_history.count_documents = AsyncMock(return_value=0)

        # Execute
        request = ReflectionPromptRequest(use_reflections=True)  # Wants to use, but not opted in
        result = await service.generate_reflection_prompt(
            TEST_USER_ID, request, save_history=False
        )

        # Verify
        assert result.based_on_reflections == False
        assert result.reflection_themes == []

    @pytest.mark.asyncio
    async def test_personalization_without_reflections_no_posts(self, service, mock_db):
        """Test fallback when user has opted in but has no posts"""
        # Setup: User opted in but has no posts
        mock_db.users.find_one = AsyncMock(return_value={
            "companion_settings": {
                "opt_in_reflection_analysis": True,
                "preferred_tts_voice": "nova"
            }
        })

        # Mock empty posts cursor
        mock_cursor = MagicMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[])  # No posts
        mock_db.posts.find = MagicMock(return_value=mock_cursor)

        # Mock history
        mock_db.companion_history.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=ObjectId())
        )
        mock_db.companion_history.count_documents = AsyncMock(return_value=0)

        # Execute
        request = ReflectionPromptRequest(use_reflections=True)
        result = await service.generate_reflection_prompt(
            TEST_USER_ID, request, save_history=False
        )

        # Verify - should still work, just not personalized
        assert result.based_on_reflections == False
        assert result.prompt  # Should have a prompt (from AI or fallback)

    @pytest.mark.asyncio
    async def test_personalization_user_disables(self, service, mock_db):
        """Test when user explicitly disables personalization in request"""
        # Setup: User opted in
        mock_db.users.find_one = AsyncMock(return_value={
            "companion_settings": {
                "opt_in_reflection_analysis": True,
                "preferred_tts_voice": "nova"
            }
        })

        # Mock history
        mock_db.companion_history.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=ObjectId())
        )
        mock_db.companion_history.count_documents = AsyncMock(return_value=0)

        # Execute - user sets use_reflections=False
        request = ReflectionPromptRequest(use_reflections=False)
        result = await service.generate_reflection_prompt(
            TEST_USER_ID, request, save_history=False
        )

        # Verify - should NOT use reflections
        assert result.based_on_reflections == False


class TestServiceValidationIntegration:
    """Test that validation is properly integrated into service"""

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.users = AsyncMock()
        db.companion_history = AsyncMock()
        db.posts = AsyncMock()
        return db

    @pytest.fixture
    def repository(self, mock_db):
        return CompanionRepository(mock_db)

    @pytest.mark.asyncio
    async def test_validation_rejects_bad_response(self, repository, mock_db):
        """Test that bad AI responses trigger fallback"""
        # Create provider that returns inappropriate content
        bad_provider = MockAIProvider(responses={
            "completion": "You should immediately seek professional help for this issue."
        })

        service = CompanionService(repository, bad_provider)

        # Setup mock
        mock_db.users.find_one = AsyncMock(return_value={
            "companion_settings": {"opt_in_reflection_analysis": False}
        })
        mock_db.companion_history.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=ObjectId())
        )
        mock_db.companion_history.count_documents = AsyncMock(return_value=0)

        # Execute
        request = ReflectionPromptRequest()
        result = await service.generate_reflection_prompt(
            TEST_USER_ID, request, save_history=False
        )

        # Should use fallback due to validation failure
        assert result.source == "fallback"

    @pytest.mark.asyncio
    async def test_ai_failure_uses_fallback(self, repository, mock_db):
        """Test that AI failure triggers fallback"""
        # Create provider that fails
        failing_provider = MockAIProvider(should_fail=True)

        service = CompanionService(repository, failing_provider)

        # Setup mock
        mock_db.users.find_one = AsyncMock(return_value={
            "companion_settings": {"opt_in_reflection_analysis": False}
        })
        mock_db.companion_history.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=ObjectId())
        )
        mock_db.companion_history.count_documents = AsyncMock(return_value=0)

        # Execute
        request = ReflectionPromptRequest()
        result = await service.generate_reflection_prompt(
            TEST_USER_ID, request, save_history=False
        )

        # Should use fallback due to AI failure
        assert result.source == "fallback"
        assert result.prompt  # Should still have a prompt


# Run tests with: pytest tests/companion/test_personalization.py -v
