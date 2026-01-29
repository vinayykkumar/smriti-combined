"""
API Router for AI Companion endpoints.

Endpoints:
- Settings management (GET/PUT)
- Reflection prompt generation (POST)
- Contemplative question generation (POST)
- Meditation guidance generation (POST)
- Text-to-speech conversion (POST)
- Conversation history (GET/DELETE)
- Reflection pattern analysis (POST)
"""

from fastapi import APIRouter, Depends, Response, HTTPException, Query
from typing import Annotated, Optional

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
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
    ConversationHistoryResponse
)
from app.companion.dependencies import (
    get_companion_service,
    rate_limit_prompt,
    rate_limit_question,
    rate_limit_meditation,
    rate_limit_tts
)
from app.companion.prompts.themes import analyze_reflection_patterns, ReflectionPatterns
from app.ai_providers.base import AIProviderError

router = APIRouter()


# ============ Settings Endpoints ============

@router.get(
    "/settings",
    response_model=CompanionSettings,
    summary="Get companion settings",
    description="Get user's AI companion settings. Creates defaults if not set."
)
async def get_settings(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Get user's companion settings."""
    settings = await service.get_settings(current_user._id)
    return settings


@router.put(
    "/settings",
    response_model=CompanionSettings,
    summary="Update companion settings",
    description="Update user's AI companion settings. Only provided fields are updated."
)
async def update_settings(
    settings_update: CompanionSettingsUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Update user's companion settings."""
    settings = await service.update_settings(current_user._id, settings_update)
    return settings


# ============ AI Generation Endpoints ============

@router.post(
    "/prompt",
    response_model=ReflectionPromptResponse,
    summary="Generate reflection prompt",
    description="""
    Generate a personalized reflection prompt.

    If user has opted in to reflection analysis, the prompt will be personalized
    based on their past reflections. Set use_reflections=false to get a generic prompt.

    Rate limited to 50 requests per hour.
    """,
    dependencies=[Depends(rate_limit_prompt)]
)
async def generate_reflection_prompt(
    request: ReflectionPromptRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Generate a personalized reflection prompt."""
    result = await service.generate_reflection_prompt(current_user._id, request)
    return result


@router.post(
    "/question",
    response_model=ContemplativeQuestionResponse,
    summary="Generate contemplative question",
    description="""
    Generate a contemplative question for self-inquiry.

    Categories: self, relationships, purpose, presence, gratitude
    Depth levels: gentle, moderate, deep

    Rate limited to 50 requests per hour.
    """,
    dependencies=[Depends(rate_limit_question)]
)
async def generate_contemplative_question(
    request: ContemplativeQuestionRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Generate a contemplative question."""
    result = await service.generate_contemplative_question(current_user._id, request)
    return result


@router.post(
    "/meditation",
    response_model=MeditationGuidanceResponse,
    summary="Generate meditation guidance",
    description="""
    Generate a meditation guidance script.

    Guidance types:
    - sankalpam: Intention setting meditation from yogic tradition
    - breath-focus: Simple breath awareness meditation
    - depth-focus: Deep contemplative meditation

    Includes opening, settling, interval, and closing guidance texts.

    Rate limited to 20 requests per hour.
    """,
    dependencies=[Depends(rate_limit_meditation)]
)
async def generate_meditation_guidance(
    request: MeditationGuidanceRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Generate meditation guidance script."""
    result = await service.generate_meditation_guidance(current_user._id, request)
    return result


@router.post(
    "/tts",
    summary="Text to speech",
    description="""
    Convert text to speech audio.

    Returns MP3 audio data.

    Available voices: alloy, echo, fable, onyx, nova, shimmer
    Speed: 0.25 to 4.0 (default 1.0)

    Rate limited to 30 requests per hour.
    """,
    dependencies=[Depends(rate_limit_tts)],
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "Audio file in MP3 format"
        },
        503: {"description": "TTS service unavailable"}
    }
)
async def text_to_speech(
    request: TTSRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Convert text to speech audio."""
    try:
        audio_bytes = await service.generate_tts(
            user_id=current_user._id,
            text=request.text,
            voice=request.voice,
            speed=request.speed
        )

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=guidance.mp3",
                "Cache-Control": "no-cache"
            }
        )

    except AIProviderError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "tts_generation_failed",
                "message": f"Text-to-speech generation failed: {e.message}"
            }
        )
    except NotImplementedError:
        raise HTTPException(
            status_code=501,
            detail={
                "error": "tts_not_supported",
                "message": "Current AI provider does not support text-to-speech"
            }
        )


# ============ Conversation History Endpoints ============

@router.get(
    "/history",
    response_model=ConversationHistoryResponse,
    summary="Get conversation history",
    description="Get paginated conversation history for the current user."
)
async def get_history(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)],
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(
        default=None,
        description="Filter by type: prompt, contemplate, meditation"
    )
):
    """Get paginated conversation history."""
    result = await service.get_history(
        user_id=current_user._id,
        page=page,
        limit=limit,
        entry_type=type
    )
    return result


@router.delete(
    "/history/{entry_id}",
    summary="Delete history entry",
    description="Delete a specific conversation history entry."
)
async def delete_history_entry(
    entry_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Delete a specific history entry."""
    deleted = await service.delete_history_entry(current_user._id, entry_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "entry_not_found",
                "message": "History entry not found or already deleted"
            }
        )

    return {"success": True, "message": "History entry deleted"}


@router.delete(
    "/history",
    summary="Delete all history",
    description="Delete all conversation history for the current user."
)
async def delete_all_history(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Delete all history for the current user."""
    deleted_count = await service.delete_all_history(current_user._id)
    return {
        "success": True,
        "message": f"Deleted {deleted_count} history entries"
    }


# ============ Analysis Endpoint ============

@router.post(
    "/analyze",
    summary="Analyze reflection patterns",
    description="""
    Analyze patterns in user's reflections.

    Returns:
    - Detected themes (gratitude, presence, seeking, etc.)
    - Emotional tone (positive, contemplative, struggling, seeking)
    - Recurring concerns across multiple reflections
    - Growth indicators (signs of positive change)

    Requires opt-in to reflection analysis.
    """
)
async def analyze_reflections(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Analyze patterns in user's reflections."""
    # Check if user has opted in
    settings = await service.get_settings(current_user._id)

    if not settings.opt_in_reflection_analysis:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "opt_in_required",
                "message": "You must opt in to reflection analysis in settings to use this feature."
            }
        )

    # Fetch user's posts
    posts = await service.repository.get_user_posts_for_context(
        current_user._id,
        limit=20
    )

    if not posts:
        return {
            "themes": [],
            "emotional_tone": "neutral",
            "recurring_concerns": [],
            "growth_indicators": [],
            "summary": "No reflections found to analyze.",
            "reflection_count": 0
        }

    # Analyze patterns
    patterns = analyze_reflection_patterns(posts)

    return {
        "themes": patterns.themes,
        "emotional_tone": patterns.emotional_tone,
        "recurring_concerns": patterns.recurring_concerns,
        "growth_indicators": patterns.growth_indicators,
        "summary": patterns.summary if patterns.summary else "Patterns detected from your reflections.",
        "reflection_count": len(posts)
    }
