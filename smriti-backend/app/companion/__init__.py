"""
AI Reflection Companion Module

This module provides AI-powered features for reflection and meditation:
- Personalized reflection prompts
- Contemplative questions
- Guided meditation with TTS
- Conversation history

Usage:
    from app.companion import router, CompanionService
    from app.companion.schemas import ReflectionPromptRequest
"""

from app.companion.router import router
from app.companion.service import CompanionService
from app.companion.schemas import (
    CompanionSettings,
    CompanionSettingsUpdate,
    ReflectionPromptRequest,
    ReflectionPromptResponse,
    ContemplativeQuestionRequest,
    ContemplativeQuestionResponse,
    MeditationGuidanceRequest,
    MeditationGuidanceResponse,
    TTSRequest,
    ConversationEntry,
    ConversationHistoryResponse
)

__all__ = [
    # Router
    "router",
    # Service
    "CompanionService",
    # Settings
    "CompanionSettings",
    "CompanionSettingsUpdate",
    # Reflection
    "ReflectionPromptRequest",
    "ReflectionPromptResponse",
    # Contemplation
    "ContemplativeQuestionRequest",
    "ContemplativeQuestionResponse",
    # Meditation
    "MeditationGuidanceRequest",
    "MeditationGuidanceResponse",
    # TTS
    "TTSRequest",
    # History
    "ConversationEntry",
    "ConversationHistoryResponse"
]
