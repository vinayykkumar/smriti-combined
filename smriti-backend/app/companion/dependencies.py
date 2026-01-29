"""
FastAPI dependencies for AI Companion module.

Provides dependency injection for the companion service and its components.
"""

from fastapi import Depends, Request
from typing import Annotated

from app.database.connection import get_database
from app.companion.repository import CompanionRepository
from app.companion.service import CompanionService
from app.ai_providers.factory import get_ai_provider
from app.ai_providers.base import AIProvider
from app.companion.rate_limiter import rate_limiter
from app.config.settings import settings


async def get_companion_repository(
    db=Depends(get_database)
) -> CompanionRepository:
    """Get companion repository instance with database connection."""
    return CompanionRepository(db)


async def get_companion_service(
    repository: Annotated[CompanionRepository, Depends(get_companion_repository)]
) -> CompanionService:
    """
    Get companion service instance with all dependencies.

    Injects:
    - Repository for database operations
    - AI provider for content generation
    """
    ai_provider = get_ai_provider()

    return CompanionService(
        repository=repository,
        ai_provider=ai_provider
    )


# Convenience type aliases for cleaner route signatures
CompanionServiceDep = Annotated[CompanionService, Depends(get_companion_service)]


# Rate limit dependencies with user context
async def rate_limit_prompt(request: Request):
    """Rate limit for prompt endpoint - uses user from request state."""
    # User ID will be set by get_current_user dependency
    user_id = getattr(getattr(request.state, 'user', None), '_id', 'anonymous')
    if hasattr(request.state, 'user') and hasattr(request.state.user, '_id'):
        user_id = request.state.user._id
    await rate_limiter.check_rate_limit(
        user_id=str(user_id),
        endpoint="prompt",
        limit=settings.COMPANION_RATE_LIMIT_PROMPT,
        window_seconds=settings.COMPANION_RATE_LIMIT_WINDOW
    )


async def rate_limit_question(request: Request):
    """Rate limit for question endpoint."""
    user_id = getattr(getattr(request.state, 'user', None), '_id', 'anonymous')
    if hasattr(request.state, 'user') and hasattr(request.state.user, '_id'):
        user_id = request.state.user._id
    await rate_limiter.check_rate_limit(
        user_id=str(user_id),
        endpoint="question",
        limit=settings.COMPANION_RATE_LIMIT_CONTEMPLATE,
        window_seconds=settings.COMPANION_RATE_LIMIT_WINDOW
    )


async def rate_limit_meditation(request: Request):
    """Rate limit for meditation endpoint."""
    user_id = getattr(getattr(request.state, 'user', None), '_id', 'anonymous')
    if hasattr(request.state, 'user') and hasattr(request.state.user, '_id'):
        user_id = request.state.user._id
    await rate_limiter.check_rate_limit(
        user_id=str(user_id),
        endpoint="meditation",
        limit=settings.COMPANION_RATE_LIMIT_MEDITATION,
        window_seconds=settings.COMPANION_RATE_LIMIT_WINDOW
    )


async def rate_limit_tts(request: Request):
    """Rate limit for TTS endpoint."""
    user_id = getattr(getattr(request.state, 'user', None), '_id', 'anonymous')
    if hasattr(request.state, 'user') and hasattr(request.state.user, '_id'):
        user_id = request.state.user._id
    await rate_limiter.check_rate_limit(
        user_id=str(user_id),
        endpoint="tts",
        limit=settings.COMPANION_RATE_LIMIT_TTS,
        window_seconds=settings.COMPANION_RATE_LIMIT_WINDOW
    )
