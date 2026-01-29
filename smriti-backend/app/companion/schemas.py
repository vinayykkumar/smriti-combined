"""
Pydantic schemas for the AI Companion module.

Defines request/response models for all companion endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, Any
from datetime import datetime


# ============ Companion Settings ============

class CompanionSettings(BaseModel):
    """User's companion settings stored in user document"""
    opt_in_reflection_analysis: bool = False
    preferred_guidance_type: Literal["sankalpam", "breath-focus", "depth-focus", "none"] = "breath-focus"
    preferred_tts_voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova"
    default_meditation_duration: int = Field(default=10, ge=1, le=60)
    show_guidance_text: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CompanionSettingsUpdate(BaseModel):
    """Partial update for companion settings"""
    opt_in_reflection_analysis: Optional[bool] = None
    preferred_guidance_type: Optional[Literal["sankalpam", "breath-focus", "depth-focus", "none"]] = None
    preferred_tts_voice: Optional[Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]] = None
    default_meditation_duration: Optional[int] = Field(default=None, ge=1, le=60)
    show_guidance_text: Optional[bool] = None


# ============ Reflection Prompt ============

class ReflectionPromptRequest(BaseModel):
    """Request for a personalized reflection prompt"""
    context: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional user-provided context or thoughts"
    )
    mood: Optional[Literal["peaceful", "contemplative", "seeking", "grateful"]] = Field(
        default=None,
        description="User's current mood to inform the prompt"
    )
    use_reflections: bool = Field(
        default=True,
        description="Whether to use past reflections for personalization (requires opt-in)"
    )


class ReflectionPromptResponse(BaseModel):
    """Response containing the generated reflection prompt"""
    prompt: str
    based_on_reflections: bool = Field(
        description="Whether past reflections were used in generation"
    )
    reflection_themes: list[str] = Field(
        default_factory=list,
        description="Themes detected from user's reflections"
    )
    source: Literal["ai", "fallback"] = Field(
        default="ai",
        description="Whether response came from AI or fallback content"
    )


# ============ Contemplative Question ============

class ContemplativeQuestionRequest(BaseModel):
    """Request for a contemplative question"""
    category: Optional[Literal["self", "relationships", "purpose", "presence", "gratitude"]] = Field(
        default=None,
        description="Category of contemplation"
    )
    depth: Literal["gentle", "moderate", "deep"] = Field(
        default="moderate",
        description="Depth level of the question"
    )
    use_reflections: bool = Field(
        default=True,
        description="Whether to use past reflections for personalization"
    )


class ContemplativeQuestionResponse(BaseModel):
    """Response containing the contemplative question"""
    question: str
    category: str
    follow_up_prompts: list[str] = Field(
        default_factory=list,
        description="Optional follow-up questions for deeper exploration"
    )
    source: Literal["ai", "fallback"] = "ai"


# ============ Meditation Guidance ============

class MeditationGuidanceRequest(BaseModel):
    """Request for meditation guidance script"""
    duration_minutes: int = Field(ge=1, le=60, description="Duration in minutes")
    guidance_type: Literal["sankalpam", "breath-focus", "depth-focus"]
    include_intervals: bool = Field(
        default=True,
        description="Include interval guidance points"
    )
    interval_minutes: int = Field(
        default=5,
        ge=1,
        le=30,
        description="Minutes between interval guidance"
    )


class MeditationGuidanceResponse(BaseModel):
    """Response containing meditation guidance"""
    opening: str = Field(description="Opening guidance text")
    settling: str = Field(description="Settling instruction (30 seconds in)")
    intervals: list[str] = Field(
        default_factory=list,
        description="Interval guidance texts"
    )
    closing: str = Field(description="Closing guidance (1 minute before end)")
    total_duration: int = Field(description="Total duration in seconds")
    source: Literal["ai", "fallback"] = "ai"


# ============ Text to Speech ============

class TTSRequest(BaseModel):
    """Request for text-to-speech conversion"""
    text: str = Field(max_length=4096, description="Text to convert to speech")
    voice: Optional[Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]] = Field(
        default=None,
        description="Voice to use (defaults to user preference)"
    )
    speed: float = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="Playback speed"
    )


# ============ Conversation History ============

class ConversationEntry(BaseModel):
    """A single conversation entry in history"""
    id: str = Field(description="Unique entry ID")
    user_id: str = Field(description="User who created this entry")
    type: Literal["prompt", "contemplate", "meditation"] = Field(
        description="Type of interaction"
    )
    request: dict[str, Any] = Field(
        description="Original request parameters"
    )
    response: dict[str, Any] = Field(
        description="AI response"
    )
    created_at: datetime


class ConversationEntryCreate(BaseModel):
    """Schema for creating a new conversation entry"""
    user_id: str
    type: Literal["prompt", "contemplate", "meditation"]
    request: dict[str, Any]
    response: dict[str, Any]


class ConversationHistoryResponse(BaseModel):
    """Paginated conversation history response"""
    entries: list[ConversationEntry]
    total: int = Field(description="Total number of entries")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Entries per page")
    has_more: bool = Field(description="Whether more entries exist")
