"""
Service layer for AI Companion.

Handles business logic for:
- Generating personalized reflection prompts
- Generating contemplative questions
- Generating meditation guidance
- Text-to-speech conversion
- Conversation history management
"""

import random
import logging
from typing import Optional

from app.companion.repository import CompanionRepository
from app.companion.schemas import (
    CompanionSettings,
    CompanionSettingsUpdate,
    ReflectionPromptRequest,
    ReflectionPromptResponse,
    ContemplativeQuestionRequest,
    ContemplativeQuestionResponse,
    MeditationGuidanceRequest,
    MeditationGuidanceResponse,
    ConversationEntry,
    ConversationEntryCreate,
    ConversationHistoryResponse
)
from app.companion.prompts import (
    COMPANION_SYSTEM_PROMPT,
    build_reflection_prompt,
    build_contemplation_prompt,
    build_meditation_prompt,
    FALLBACK_REFLECTION_PROMPTS,
    FALLBACK_QUESTIONS,
    FALLBACK_MEDITATION,
    extract_themes,
    summarize_posts_for_context,
    analyze_reflection_patterns,
    build_personalized_context,
    clean_response,
    parse_question_response,
    parse_meditation_response
)
from app.companion.validation import (
    validate_response,
    validate_reflection_prompt,
    validate_contemplative_question,
    validate_meditation_guidance
)
from app.ai_providers.base import AIProvider, AIProviderError
from app.config.settings import settings

logger = logging.getLogger(__name__)


class CompanionService:
    """Service for AI companion features"""

    def __init__(
        self,
        repository: CompanionRepository,
        ai_provider: AIProvider
    ):
        self.repository = repository
        self.ai_provider = ai_provider

    # ============ Settings ============

    async def get_settings(self, user_id: str) -> CompanionSettings:
        """Get user's companion settings, creating defaults if needed"""
        settings_obj = await self.repository.get_settings(user_id)
        if not settings_obj:
            settings_obj = await self.repository.create_default_settings(user_id)
        return settings_obj

    async def update_settings(
        self,
        user_id: str,
        update: CompanionSettingsUpdate
    ) -> CompanionSettings:
        """Update user's companion settings"""
        return await self.repository.update_settings(user_id, update)

    # ============ Reflection Prompt ============

    async def generate_reflection_prompt(
        self,
        user_id: str,
        request: ReflectionPromptRequest,
        save_history: bool = True
    ) -> ReflectionPromptResponse:
        """
        Generate a personalized reflection prompt.

        Personalization flow:
        1. Check if user opted in AND request wants to use reflections
        2. Fetch user's recent posts/reflections
        3. Analyze patterns: themes, emotional tone, recurring concerns
        4. Build personalized context for AI prompt
        5. Generate response with fallback handling
        6. Validate response for appropriateness
        7. Save to history if requested

        Args:
            user_id: User's ID
            request: Prompt request parameters
            save_history: Whether to save to conversation history

        Returns:
            ReflectionPromptResponse with generated prompt
        """
        user_settings = await self.get_settings(user_id)

        # Determine if we should use past reflections
        user_context = None
        reflection_themes = []
        patterns = None

        should_use_reflections = (
            request.use_reflections and
            user_settings.opt_in_reflection_analysis
        )

        if should_use_reflections:
            # Fetch user's recent posts for context
            posts = await self.repository.get_user_posts_for_context(user_id, limit=10)

            if posts:
                # Analyze patterns in their reflections
                patterns = analyze_reflection_patterns(posts)
                reflection_themes = patterns.themes

                # Build rich personalized context
                user_context = build_personalized_context(posts)

                logger.debug(
                    f"Personalization for user {user_id}: "
                    f"themes={reflection_themes}, tone={patterns.emotional_tone}"
                )

        try:
            # Build and send prompt to AI
            ai_prompt = build_reflection_prompt(
                user_context=user_context,
                mood=request.mood,
                additional_context=request.context
            )

            response_text = await self.ai_provider.generate_completion(
                system_prompt=COMPANION_SYSTEM_PROMPT,
                user_prompt=ai_prompt,
                max_tokens=300,
                temperature=0.8
            )

            # Clean the response
            response_text = clean_response(response_text)

            # Validate response for appropriateness
            validation = validate_reflection_prompt(response_text)

            if not validation.is_valid:
                logger.warning(
                    f"AI response failed validation: {validation.issues}. Using fallback."
                )
                raise AIProviderError(
                    "Response validation failed",
                    provider="validation"
                )

            if validation.severity == "warning":
                logger.info(f"Response validation warnings: {validation.issues}")

            result = ReflectionPromptResponse(
                prompt=response_text,
                based_on_reflections=user_context is not None,
                reflection_themes=reflection_themes,
                source="ai"
            )

        except (AIProviderError, Exception) as e:
            logger.warning(f"AI generation failed, using fallback: {e}")
            result = ReflectionPromptResponse(
                prompt=random.choice(FALLBACK_REFLECTION_PROMPTS),
                based_on_reflections=False,
                reflection_themes=[],
                source="fallback"
            )

        # Save to history
        if save_history:
            await self._save_history(
                user_id=user_id,
                entry_type="prompt",
                request=request.model_dump(),
                response=result.model_dump()
            )

        return result

    # ============ Contemplative Question ============

    async def generate_contemplative_question(
        self,
        user_id: str,
        request: ContemplativeQuestionRequest,
        save_history: bool = True
    ) -> ContemplativeQuestionResponse:
        """
        Generate a contemplative question.

        Personalization flow:
        1. Check opt-in status and request preference
        2. Fetch recent reflections if allowed
        3. Build personalized context with emotional awareness
        4. Generate question with category and depth guidance
        5. Validate and return with follow-ups

        Args:
            user_id: User's ID
            request: Question request parameters
            save_history: Whether to save to conversation history

        Returns:
            ContemplativeQuestionResponse with generated question
        """
        user_settings = await self.get_settings(user_id)

        # Get context if opted in and requested
        user_context = None
        should_use_reflections = (
            request.use_reflections and
            user_settings.opt_in_reflection_analysis
        )

        if should_use_reflections:
            posts = await self.repository.get_user_posts_for_context(user_id, limit=5)
            if posts:
                # Use lighter context for questions (less text, more patterns)
                patterns = analyze_reflection_patterns(posts)
                if patterns.summary:
                    user_context = f"This person is {patterns.summary}."

        try:
            ai_prompt = build_contemplation_prompt(
                category=request.category,
                depth=request.depth,
                user_context=user_context
            )

            response_text = await self.ai_provider.generate_completion(
                system_prompt=COMPANION_SYSTEM_PROMPT,
                user_prompt=ai_prompt,
                max_tokens=400,
                temperature=0.8
            )

            # Parse the JSON response
            parsed = parse_question_response(response_text)
            question = parsed["question"]

            # Validate the question
            validation = validate_contemplative_question(question)

            if not validation.is_valid:
                logger.warning(
                    f"Question validation failed: {validation.issues}. Using fallback."
                )
                raise AIProviderError(
                    "Question validation failed",
                    provider="validation"
                )

            category = request.category or "general"

            result = ContemplativeQuestionResponse(
                question=question,
                category=category,
                follow_up_prompts=parsed.get("follow_ups", []),
                source="ai"
            )

        except (AIProviderError, Exception) as e:
            logger.warning(f"AI generation failed, using fallback: {e}")
            category = request.category or "presence"
            fallback_list = FALLBACK_QUESTIONS.get(category, FALLBACK_QUESTIONS["presence"])

            result = ContemplativeQuestionResponse(
                question=random.choice(fallback_list),
                category=category,
                follow_up_prompts=[],
                source="fallback"
            )

        # Save to history
        if save_history:
            await self._save_history(
                user_id=user_id,
                entry_type="contemplate",
                request=request.model_dump(),
                response=result.model_dump()
            )

        return result

    # ============ Meditation Guidance ============

    async def generate_meditation_guidance(
        self,
        user_id: str,
        request: MeditationGuidanceRequest,
        save_history: bool = True
    ) -> MeditationGuidanceResponse:
        """
        Generate meditation guidance script.

        Note: Meditation guidance is NOT personalized with past reflections
        as it should be consistent with the meditation type's tradition.

        Args:
            user_id: User's ID
            request: Meditation request parameters
            save_history: Whether to save to conversation history

        Returns:
            MeditationGuidanceResponse with guidance script
        """
        # Calculate number of intervals
        num_intervals = 0
        if request.include_intervals and request.interval_minutes:
            num_intervals = (request.duration_minutes // request.interval_minutes) - 1
            num_intervals = max(0, min(num_intervals, 10))  # Cap at 10

        try:
            ai_prompt = build_meditation_prompt(
                guidance_type=request.guidance_type,
                duration_minutes=request.duration_minutes,
                num_intervals=num_intervals
            )

            response_text = await self.ai_provider.generate_completion(
                system_prompt=COMPANION_SYSTEM_PROMPT,
                user_prompt=ai_prompt,
                max_tokens=1500,
                temperature=0.7
            )

            # Parse the JSON response
            parsed = parse_meditation_response(response_text)

            # Validate the meditation guidance
            validation = validate_meditation_guidance(parsed)

            if not validation.is_valid:
                logger.warning(
                    f"Meditation validation failed: {validation.issues}. Using fallback."
                )
                raise AIProviderError(
                    "Meditation validation failed",
                    provider="validation"
                )

            result = MeditationGuidanceResponse(
                opening=parsed["opening"],
                settling=parsed["settling"],
                intervals=parsed["intervals"][:num_intervals] if num_intervals > 0 else [],
                closing=parsed["closing"],
                total_duration=request.duration_minutes * 60,
                source="ai"
            )

        except (AIProviderError, Exception) as e:
            logger.warning(f"AI generation failed, using fallback: {e}")
            fallback = FALLBACK_MEDITATION.get(
                request.guidance_type,
                FALLBACK_MEDITATION["breath-focus"]
            )

            result = MeditationGuidanceResponse(
                opening=fallback["opening"],
                settling=fallback["settling"],
                intervals=fallback["intervals"][:num_intervals] if num_intervals > 0 else [],
                closing=fallback["closing"],
                total_duration=request.duration_minutes * 60,
                source="fallback"
            )

        # Save to history
        if save_history:
            await self._save_history(
                user_id=user_id,
                entry_type="meditation",
                request=request.model_dump(),
                response=result.model_dump()
            )

        return result

    # ============ Text to Speech ============

    async def generate_tts(
        self,
        user_id: str,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0
    ) -> bytes:
        """
        Generate text-to-speech audio.

        Args:
            user_id: User's ID
            text: Text to convert
            voice: Voice to use (defaults to user preference)
            speed: Playback speed

        Returns:
            Audio bytes (MP3 format)
        """
        # Get user's preferred voice if not specified
        if not voice:
            user_settings = await self.get_settings(user_id)
            voice = user_settings.preferred_tts_voice

        return await self.ai_provider.generate_tts(text, voice, speed)

    # ============ Conversation History ============

    async def get_history(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        entry_type: Optional[str] = None
    ) -> ConversationHistoryResponse:
        """Get paginated conversation history"""
        entries, total = await self.repository.get_history(
            user_id=user_id,
            page=page,
            limit=limit,
            entry_type=entry_type
        )

        has_more = (page * limit) < total

        return ConversationHistoryResponse(
            entries=entries,
            total=total,
            page=page,
            limit=limit,
            has_more=has_more
        )

    async def delete_history_entry(self, user_id: str, entry_id: str) -> bool:
        """Delete a specific history entry"""
        return await self.repository.delete_history_entry(entry_id, user_id)

    async def delete_all_history(self, user_id: str) -> int:
        """Delete all history for a user"""
        return await self.repository.delete_all_history(user_id)

    # ============ Helper Methods ============

    async def _save_history(
        self,
        user_id: str,
        entry_type: str,
        request: dict,
        response: dict
    ):
        """Save interaction to conversation history"""
        try:
            entry = ConversationEntryCreate(
                user_id=user_id,
                type=entry_type,
                request=request,
                response=response
            )
            await self.repository.add_history_entry(entry)

            # Enforce max entries limit
            await self.repository.enforce_max_entries(
                user_id,
                settings.COMPANION_HISTORY_MAX_ENTRIES
            )
        except Exception as e:
            # Don't fail the main request if history save fails
            logger.error(f"Failed to save history: {e}")
