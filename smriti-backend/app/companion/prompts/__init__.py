"""
Prompt Templates for AI Companion

This module contains all prompt templates and the system prompt
that defines the companion's personality.

Templates are stored in code for:
- Version control
- Easy testing
- Type safety
- No external dependencies

Usage:
    from app.companion.prompts import (
        COMPANION_SYSTEM_PROMPT,
        build_reflection_prompt,
        build_contemplation_prompt,
        build_meditation_prompt,
        FALLBACK_PROMPTS
    )
"""

from app.companion.prompts.system import COMPANION_SYSTEM_PROMPT
from app.companion.prompts.reflection import (
    build_reflection_prompt,
    FALLBACK_REFLECTION_PROMPTS
)
from app.companion.prompts.contemplation import (
    build_contemplation_prompt,
    FALLBACK_QUESTIONS
)
from app.companion.prompts.meditation import (
    build_meditation_prompt,
    FALLBACK_MEDITATION
)
from app.companion.prompts.themes import (
    extract_themes,
    summarize_posts_for_context,
    analyze_reflection_patterns,
    build_personalized_context,
    detect_emotional_tone,
    ReflectionPatterns
)
from app.companion.prompts.parsing import (
    clean_response,
    parse_question_response,
    parse_meditation_response
)

__all__ = [
    # System
    "COMPANION_SYSTEM_PROMPT",
    # Reflection
    "build_reflection_prompt",
    "FALLBACK_REFLECTION_PROMPTS",
    # Contemplation
    "build_contemplation_prompt",
    "FALLBACK_QUESTIONS",
    # Meditation
    "build_meditation_prompt",
    "FALLBACK_MEDITATION",
    # Themes & Patterns
    "extract_themes",
    "summarize_posts_for_context",
    "analyze_reflection_patterns",
    "build_personalized_context",
    "detect_emotional_tone",
    "ReflectionPatterns",
    # Parsing
    "clean_response",
    "parse_question_response",
    "parse_meditation_response"
]
