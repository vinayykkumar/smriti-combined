# AI Reflection Companion - Backend Schema & API Design

## Document Info
- **Feature**: AI Reflection Companion
- **Phase**: Backend API Design
- **Created**: 2026-01-28
- **Status**: Complete

---

## 1. Database Schema

### 1.1 User Schema Extension

Add companion-related fields to existing `users` collection:

```python
# Addition to existing user document
{
    # ... existing user fields ...

    "companion_settings": {
        "opt_in_reflection_analysis": False,  # Explicit opt-in required
        "preferred_guidance_type": "breath",   # breath | body-scan | loving-kindness
        "preferred_tts_voice": "nova",         # OpenAI voice selection
        "preferred_ambient_sound": "rain",     # Default ambient sound
        "default_meditation_duration": 10,     # Minutes
        "show_guidance_text": True,            # Show text while TTS plays
        "created_at": datetime,
        "updated_at": datetime
    }
}
```

### 1.2 Companion Settings Schema (Pydantic)

```python
# app/companion/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class CompanionSettings(BaseModel):
    opt_in_reflection_analysis: bool = False
    preferred_guidance_type: Literal["sankalpam", "breath-focus", "depth-focus", "none"] = "breath-focus"
    preferred_tts_voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova"
    preferred_ambient_sound: Literal["silence", "tibetan-bowl"] = "silence"
    default_meditation_duration: int = Field(default=10, ge=1, le=60)
    show_guidance_text: bool = True

class CompanionSettingsUpdate(BaseModel):
    opt_in_reflection_analysis: Optional[bool] = None
    preferred_guidance_type: Optional[Literal["sankalpam", "breath-focus", "depth-focus", "none"]] = None
    preferred_tts_voice: Optional[Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]] = None
    preferred_ambient_sound: Optional[Literal["silence", "tibetan-bowl"]] = None
    default_meditation_duration: Optional[int] = Field(default=None, ge=1, le=60)
    show_guidance_text: Optional[bool] = None

class CompanionSettingsResponse(CompanionSettings):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

---

## 2. API Endpoints

### 2.1 Endpoint Summary

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/companion/settings` | GET | Get user's companion settings | Required |
| `/api/companion/settings` | PUT | Update companion settings | Required |
| `/api/companion/prompt` | POST | Get personalized reflection prompt | Required |
| `/api/companion/question` | POST | Get contemplative question | Required |
| `/api/companion/meditation` | POST | Get meditation guidance script | Required |
| `/api/companion/tts` | POST | Convert text to speech | Required |

### 2.2 Request/Response Schemas

#### Settings Endpoints

```python
# GET /api/companion/settings
# Response:
{
    "success": True,
    "data": {
        "opt_in_reflection_analysis": False,
        "preferred_guidance_type": "breath",
        "preferred_tts_voice": "nova",
        "preferred_ambient_sound": "rain",
        "default_meditation_duration": 10,
        "show_guidance_text": True,
        "created_at": "2026-01-28T10:00:00Z",
        "updated_at": "2026-01-28T10:00:00Z"
    }
}

# PUT /api/companion/settings
# Request:
{
    "opt_in_reflection_analysis": True,
    "preferred_guidance_type": "body-scan"
}
# Response: Same as GET
```

#### Reflection Prompt Endpoint

```python
# POST /api/companion/prompt
# Request:
class ReflectionPromptRequest(BaseModel):
    context: Optional[str] = None  # Optional user-provided context
    mood: Optional[Literal["peaceful", "contemplative", "seeking", "grateful"]] = None

# Response:
class ReflectionPromptResponse(BaseModel):
    prompt: str                    # The generated reflection prompt
    based_on_reflections: bool     # Whether past reflections were used
    reflection_themes: list[str]   # Themes detected (if opted in)

# Example Response:
{
    "success": True,
    "data": {
        "prompt": "You've been exploring themes of impermanence in your recent reflections. Today, consider: What in your life right now feels temporary, and how does acknowledging that change your relationship with it?",
        "based_on_reflections": True,
        "reflection_themes": ["impermanence", "acceptance", "presence"]
    }
}
```

#### Contemplative Question Endpoint

```python
# POST /api/companion/question
# Request:
class ContemplativeQuestionRequest(BaseModel):
    category: Optional[Literal["self", "relationships", "purpose", "presence", "gratitude"]] = None
    depth: Optional[Literal["gentle", "moderate", "deep"]] = "moderate"

# Response:
class ContemplativeQuestionResponse(BaseModel):
    question: str
    category: str
    follow_up_prompts: list[str]  # 2-3 optional follow-up questions

# Example Response:
{
    "success": True,
    "data": {
        "question": "What truth about yourself have you been avoiding, and what would change if you gently acknowledged it?",
        "category": "self",
        "follow_up_prompts": [
            "How does this truth connect to your deepest values?",
            "What support would help you face this with compassion?"
        ]
    }
}
```

#### Meditation Guidance Endpoint

```python
# POST /api/companion/meditation
# Request:
class MeditationGuidanceRequest(BaseModel):
    duration_minutes: int = Field(ge=1, le=60)
    guidance_type: Literal["sankalpam", "breath-focus", "depth-focus"]
    include_intervals: bool = True
    interval_minutes: Optional[int] = Field(default=5, ge=1, le=30)

# Response:
class MeditationGuidanceResponse(BaseModel):
    opening: str           # Opening guidance text (spoken at start)
    settling: str          # Settling instruction (30 seconds in)
    intervals: list[str]   # Interval guidance texts
    closing: str           # Closing guidance (1 minute before end)
    total_duration: int    # Confirmed duration in seconds

# Example Response:
{
    "success": True,
    "data": {
        "opening": "Welcome to this moment of stillness. Allow your body to settle into a comfortable position. There is nowhere else you need to be right now.",
        "settling": "Begin to notice your breath, without trying to change it. Simply observe the natural rhythm of inhaling and exhaling.",
        "intervals": [
            "Gently return your attention to your breath. If your mind has wandered, that's perfectly natural. Simply begin again.",
            "Notice any areas of tension in your body. With each exhale, invite those areas to soften.",
            "You're doing beautifully. Continue resting in this present moment."
        ],
        "closing": "Begin to deepen your breath slightly. Slowly bring your awareness back to the room around you. When you're ready, gently open your eyes.",
        "total_duration": 600
    }
}
```

#### Text-to-Speech Endpoint

```python
# POST /api/companion/tts
# Request:
class TTSRequest(BaseModel):
    text: str = Field(max_length=4096)  # OpenAI TTS limit
    voice: Optional[Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]] = None

# Response: Audio file (MP3)
# Content-Type: audio/mpeg
# Returns raw audio bytes

# Error Response:
{
    "success": False,
    "error": {
        "code": "TTS_ERROR",
        "message": "Failed to generate speech"
    }
}
```

---

## 3. API Implementation Details

### 3.1 Router (router.py)

```python
# app/companion/router.py

from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from typing import Annotated

from app.auth.dependencies import get_current_user
from app.companion.service import CompanionService
from app.companion.schemas import (
    CompanionSettingsResponse,
    CompanionSettingsUpdate,
    ReflectionPromptRequest,
    ReflectionPromptResponse,
    ContemplativeQuestionRequest,
    ContemplativeQuestionResponse,
    MeditationGuidanceRequest,
    MeditationGuidanceResponse,
    TTSRequest
)
from app.companion.dependencies import get_companion_service
from app.utils.response_formatter import format_response

router = APIRouter(prefix="/api/companion", tags=["companion"])

@router.get("/settings", response_model=CompanionSettingsResponse)
async def get_settings(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Get user's companion settings"""
    settings = await service.get_settings(current_user["_id"])
    return format_response(settings)

@router.put("/settings", response_model=CompanionSettingsResponse)
async def update_settings(
    settings_update: CompanionSettingsUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Update user's companion settings"""
    settings = await service.update_settings(current_user["_id"], settings_update)
    return format_response(settings)

@router.post("/prompt", response_model=ReflectionPromptResponse)
async def get_reflection_prompt(
    request: ReflectionPromptRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Get a personalized reflection prompt"""
    result = await service.generate_reflection_prompt(current_user["_id"], request)
    return format_response(result)

@router.post("/question", response_model=ContemplativeQuestionResponse)
async def get_contemplative_question(
    request: ContemplativeQuestionRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Get a contemplative question"""
    result = await service.generate_contemplative_question(current_user["_id"], request)
    return format_response(result)

@router.post("/meditation", response_model=MeditationGuidanceResponse)
async def get_meditation_guidance(
    request: MeditationGuidanceRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Get meditation guidance script"""
    result = await service.generate_meditation_guidance(current_user["_id"], request)
    return format_response(result)

@router.post("/tts")
async def text_to_speech(
    request: TTSRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Convert text to speech audio"""
    # Get user's preferred voice if not specified
    voice = request.voice
    if not voice:
        settings = await service.get_settings(current_user["_id"])
        voice = settings.preferred_tts_voice

    audio_bytes = await service.generate_tts(request.text, voice)

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=guidance.mp3"
        }
    )
```

### 3.2 Service Layer (service.py)

```python
# app/companion/service.py

from typing import Optional
from bson import ObjectId
from datetime import datetime

from app.companion.schemas import (
    CompanionSettings,
    CompanionSettingsUpdate,
    ReflectionPromptRequest,
    ReflectionPromptResponse,
    ContemplativeQuestionRequest,
    ContemplativeQuestionResponse,
    MeditationGuidanceRequest,
    MeditationGuidanceResponse
)
from app.companion.repository import CompanionRepository
from app.companion.prompts.reflection import build_reflection_prompt
from app.companion.prompts.contemplation import build_contemplation_prompt
from app.companion.prompts.meditation import build_meditation_prompt
from app.companion.prompts.system import COMPANION_SYSTEM_PROMPT
from app.ai_providers.base import AIProvider
from app.posts.repository import PostRepository

class CompanionService:
    def __init__(
        self,
        repository: CompanionRepository,
        post_repository: PostRepository,
        ai_provider: AIProvider
    ):
        self.repository = repository
        self.post_repository = post_repository
        self.ai_provider = ai_provider

    async def get_settings(self, user_id: ObjectId) -> CompanionSettings:
        """Get user's companion settings, creating defaults if needed"""
        settings = await self.repository.get_settings(user_id)
        if not settings:
            settings = await self.repository.create_default_settings(user_id)
        return settings

    async def update_settings(
        self,
        user_id: ObjectId,
        update: CompanionSettingsUpdate
    ) -> CompanionSettings:
        """Update user's companion settings"""
        return await self.repository.update_settings(user_id, update)

    async def generate_reflection_prompt(
        self,
        user_id: ObjectId,
        request: ReflectionPromptRequest
    ) -> ReflectionPromptResponse:
        """Generate a personalized reflection prompt"""
        settings = await self.get_settings(user_id)

        # Get user's recent reflections if opted in
        user_context = None
        reflection_themes = []

        if settings.opt_in_reflection_analysis:
            recent_posts = await self.post_repository.get_user_posts(
                user_id=user_id,
                limit=10,
                sort_by="created_at",
                sort_order=-1
            )
            if recent_posts:
                user_context = self._extract_reflection_context(recent_posts)
                reflection_themes = self._extract_themes(recent_posts)

        # Build the prompt for AI
        ai_prompt = build_reflection_prompt(
            user_context=user_context,
            mood=request.mood,
            additional_context=request.context
        )

        # Generate response from AI
        response = await self.ai_provider.generate_completion(
            system_prompt=COMPANION_SYSTEM_PROMPT,
            user_prompt=ai_prompt,
            max_tokens=300
        )

        return ReflectionPromptResponse(
            prompt=response,
            based_on_reflections=user_context is not None,
            reflection_themes=reflection_themes
        )

    async def generate_contemplative_question(
        self,
        user_id: ObjectId,
        request: ContemplativeQuestionRequest
    ) -> ContemplativeQuestionResponse:
        """Generate a contemplative question"""
        settings = await self.get_settings(user_id)

        # Optionally use reflection context
        user_context = None
        if settings.opt_in_reflection_analysis:
            recent_posts = await self.post_repository.get_user_posts(
                user_id=user_id,
                limit=5,
                sort_by="created_at",
                sort_order=-1
            )
            if recent_posts:
                user_context = self._extract_reflection_context(recent_posts)

        # Build prompt
        ai_prompt = build_contemplation_prompt(
            category=request.category,
            depth=request.depth,
            user_context=user_context
        )

        # Generate response
        response = await self.ai_provider.generate_completion(
            system_prompt=COMPANION_SYSTEM_PROMPT,
            user_prompt=ai_prompt,
            max_tokens=400
        )

        # Parse response (AI returns JSON-structured response)
        parsed = self._parse_question_response(response)

        return ContemplativeQuestionResponse(
            question=parsed["question"],
            category=request.category or "general",
            follow_up_prompts=parsed.get("follow_ups", [])
        )

    async def generate_meditation_guidance(
        self,
        user_id: ObjectId,
        request: MeditationGuidanceRequest
    ) -> MeditationGuidanceResponse:
        """Generate meditation guidance script"""

        # Calculate number of intervals
        num_intervals = 0
        if request.include_intervals and request.interval_minutes:
            num_intervals = (request.duration_minutes // request.interval_minutes) - 1
            num_intervals = max(0, min(num_intervals, 10))  # Cap at 10 intervals

        # Build prompt
        ai_prompt = build_meditation_prompt(
            guidance_type=request.guidance_type,
            duration_minutes=request.duration_minutes,
            num_intervals=num_intervals
        )

        # Generate response
        response = await self.ai_provider.generate_completion(
            system_prompt=COMPANION_SYSTEM_PROMPT,
            user_prompt=ai_prompt,
            max_tokens=1000
        )

        # Parse response
        parsed = self._parse_meditation_response(response)

        return MeditationGuidanceResponse(
            opening=parsed["opening"],
            settling=parsed["settling"],
            intervals=parsed["intervals"][:num_intervals],
            closing=parsed["closing"],
            total_duration=request.duration_minutes * 60
        )

    async def generate_tts(self, text: str, voice: str) -> bytes:
        """Generate text-to-speech audio"""
        return await self.ai_provider.generate_tts(text=text, voice=voice)

    def _extract_reflection_context(self, posts: list) -> str:
        """Extract context from user's posts for AI"""
        texts = []
        for post in posts[:10]:
            content = post.get("content", "")
            if content:
                # Truncate long posts
                texts.append(content[:500])
        return "\n---\n".join(texts)

    def _extract_themes(self, posts: list) -> list[str]:
        """Extract themes from posts (simple keyword extraction)"""
        # This could be enhanced with NLP or AI-based extraction
        themes = set()
        theme_keywords = {
            "gratitude": ["grateful", "thankful", "appreciation", "blessed"],
            "presence": ["present", "moment", "now", "awareness", "mindful"],
            "impermanence": ["change", "temporary", "passing", "letting go"],
            "compassion": ["compassion", "kindness", "love", "caring"],
            "growth": ["growth", "learning", "evolving", "becoming"],
            "peace": ["peace", "calm", "stillness", "quiet", "serene"],
            "acceptance": ["accept", "embrace", "allow", "surrender"]
        }

        all_text = " ".join(p.get("content", "").lower() for p in posts)

        for theme, keywords in theme_keywords.items():
            if any(kw in all_text for kw in keywords):
                themes.add(theme)

        return list(themes)[:5]

    def _parse_question_response(self, response: str) -> dict:
        """Parse AI response for question generation"""
        # AI is prompted to return structured format
        # This parses or falls back gracefully
        import json
        try:
            return json.loads(response)
        except:
            return {
                "question": response.strip(),
                "follow_ups": []
            }

    def _parse_meditation_response(self, response: str) -> dict:
        """Parse AI response for meditation guidance"""
        import json
        try:
            return json.loads(response)
        except:
            # Fallback: treat entire response as opening
            return {
                "opening": response.strip(),
                "settling": "Allow your breath to find its natural rhythm.",
                "intervals": ["Gently return your attention to the present moment."],
                "closing": "Slowly bring your awareness back to the room around you."
            }
```

### 3.3 Repository Layer (repository.py)

```python
# app/companion/repository.py

from typing import Optional
from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.companion.schemas import CompanionSettings, CompanionSettingsUpdate

class CompanionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users_collection = db.users

    async def get_settings(self, user_id: ObjectId) -> Optional[CompanionSettings]:
        """Get companion settings for a user"""
        user = await self.users_collection.find_one(
            {"_id": user_id},
            {"companion_settings": 1}
        )

        if user and "companion_settings" in user:
            return CompanionSettings(**user["companion_settings"])
        return None

    async def create_default_settings(self, user_id: ObjectId) -> CompanionSettings:
        """Create default companion settings for a user"""
        default_settings = CompanionSettings()
        now = datetime.utcnow()

        settings_dict = default_settings.model_dump()
        settings_dict["created_at"] = now
        settings_dict["updated_at"] = now

        await self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {"companion_settings": settings_dict}}
        )

        return default_settings

    async def update_settings(
        self,
        user_id: ObjectId,
        update: CompanionSettingsUpdate
    ) -> CompanionSettings:
        """Update companion settings for a user"""
        # Get current settings or create defaults
        current = await self.get_settings(user_id)
        if not current:
            current = await self.create_default_settings(user_id)

        # Apply updates
        update_dict = update.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()

        await self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {f"companion_settings.{k}": v for k, v in update_dict.items()}}
        )

        # Return updated settings
        return await self.get_settings(user_id)
```

### 3.4 Dependencies (dependencies.py)

```python
# app/companion/dependencies.py

from fastapi import Depends
from typing import Annotated

from app.database.connection import get_database
from app.companion.repository import CompanionRepository
from app.companion.service import CompanionService
from app.posts.repository import PostRepository
from app.ai_providers.factory import get_ai_provider
from app.ai_providers.base import AIProvider

async def get_companion_repository(
    db: Annotated[any, Depends(get_database)]
) -> CompanionRepository:
    return CompanionRepository(db)

async def get_companion_service(
    repository: Annotated[CompanionRepository, Depends(get_companion_repository)],
    post_repository: Annotated[PostRepository, Depends()],
    ai_provider: Annotated[AIProvider, Depends(get_ai_provider)]
) -> CompanionService:
    return CompanionService(
        repository=repository,
        post_repository=post_repository,
        ai_provider=ai_provider
    )
```

---

## 4. Error Handling

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `COMPANION_SETTINGS_NOT_FOUND` | 404 | Settings not found (shouldn't happen, auto-created) |
| `AI_PROVIDER_ERROR` | 503 | AI provider unavailable or error |
| `TTS_GENERATION_ERROR` | 500 | TTS generation failed |
| `INVALID_VOICE` | 400 | Invalid TTS voice selection |
| `TEXT_TOO_LONG` | 400 | TTS text exceeds limit |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

### Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/companion/prompt` | 20 requests | per hour |
| `/companion/question` | 20 requests | per hour |
| `/companion/meditation` | 10 requests | per hour |
| `/companion/tts` | 30 requests | per hour |

---

## 5. Configuration (settings.py additions)

```python
# app/config/settings.py (additions)

class Settings(BaseSettings):
    # ... existing settings ...

    # AI Provider Settings
    AI_PROVIDER: str = "openai"  # openai | anthropic | local

    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"  # Cost-effective default
    OPENAI_TTS_MODEL: str = "tts-1"
    OPENAI_TTS_VOICE: str = "nova"

    # Anthropic Settings (optional)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"

    # Local Model Settings (optional)
    LOCAL_MODEL_URL: str = "http://localhost:11434"
    LOCAL_MODEL_NAME: str = "llama3"

    # Companion Rate Limits
    COMPANION_RATE_LIMIT_PROMPT: int = 20
    COMPANION_RATE_LIMIT_QUESTION: int = 20
    COMPANION_RATE_LIMIT_MEDITATION: int = 10
    COMPANION_RATE_LIMIT_TTS: int = 30
    COMPANION_RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
```

---

## 6. Main App Registration

```python
# app/main.py (addition)

from app.companion.router import router as companion_router

# Add to existing routers
app.include_router(companion_router)
```

---

## 7. Testing Considerations

### Unit Tests
- Test settings CRUD operations
- Test prompt building functions
- Test AI response parsing
- Test theme extraction

### Integration Tests
- Test full endpoint flow with mocked AI provider
- Test rate limiting
- Test error handling

### Mock AI Provider for Testing
```python
class MockAIProvider(AIProvider):
    async def generate_completion(self, system_prompt, user_prompt, max_tokens):
        return "This is a mock reflection prompt for testing."

    async def generate_tts(self, text, voice):
        return b"mock audio bytes"
```
