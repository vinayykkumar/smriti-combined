# AI Reflection Companion - Backend Implementation Plan

## Document Info
- **Feature**: AI Reflection Companion
- **Phase**: Backend Implementation Plan
- **Created**: 2026-01-28
- **Status**: Complete

---

## 1. Implementation Order

The backend should be implemented in this order to enable incremental testing:

```
Phase 1: Foundation
├── 1.1 Configuration & Settings
├── 1.2 AI Provider Base & Factory
└── 1.3 OpenAI Provider Implementation

Phase 2: Core Module
├── 2.1 Companion Schemas
├── 2.2 Companion Repository
├── 2.3 Prompt Templates
└── 2.4 Companion Service

Phase 3: API Layer
├── 3.1 Companion Router
├── 3.2 Dependencies
└── 3.3 Main App Registration

Phase 4: Polish
├── 4.1 Error Handling
├── 4.2 Rate Limiting
└── 4.3 Testing
```

---

## 2. Phase 1: Foundation

### 2.1 Configuration & Settings

**File**: `app/config/settings.py`

**Changes**:
```python
# Add to existing Settings class

# AI Provider Configuration
AI_PROVIDER: str = Field(default="openai", env="AI_PROVIDER")

# OpenAI Configuration
OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
OPENAI_MODEL: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
OPENAI_TTS_MODEL: str = Field(default="tts-1", env="OPENAI_TTS_MODEL")
OPENAI_TTS_VOICE: str = Field(default="nova", env="OPENAI_TTS_VOICE")

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
ANTHROPIC_MODEL: str = Field(default="claude-3-haiku-20240307", env="ANTHROPIC_MODEL")

# Local Model Configuration (optional)
LOCAL_MODEL_URL: str = Field(default="http://localhost:11434", env="LOCAL_MODEL_URL")
LOCAL_MODEL_NAME: str = Field(default="llama3", env="LOCAL_MODEL_NAME")

# Companion Rate Limits
COMPANION_RATE_LIMIT_PROMPT: int = Field(default=20, env="COMPANION_RATE_LIMIT_PROMPT")
COMPANION_RATE_LIMIT_QUESTION: int = Field(default=20, env="COMPANION_RATE_LIMIT_QUESTION")
COMPANION_RATE_LIMIT_MEDITATION: int = Field(default=10, env="COMPANION_RATE_LIMIT_MEDITATION")
COMPANION_RATE_LIMIT_TTS: int = Field(default=30, env="COMPANION_RATE_LIMIT_TTS")
COMPANION_RATE_LIMIT_WINDOW: int = Field(default=3600, env="COMPANION_RATE_LIMIT_WINDOW")
```

**Environment File** (`.env.example`):
```bash
# AI Companion Configuration
AI_PROVIDER=openai

# OpenAI (required if AI_PROVIDER=openai)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=nova

# Anthropic (optional)
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Local Ollama (optional)
LOCAL_MODEL_URL=http://localhost:11434
LOCAL_MODEL_NAME=llama3
```

---

### 2.2 AI Provider Base & Factory

**Create Directory**:
```bash
mkdir -p app/ai_providers
```

**Files to Create**:

1. `app/ai_providers/__init__.py`
2. `app/ai_providers/base.py`
3. `app/ai_providers/factory.py`
4. `app/ai_providers/config.py`

**Implementation**: See `03-ai-providers.md` for full code.

**Verification Test**:
```python
# Quick test to verify factory works
from app.ai_providers import AIProviderFactory

# Should not raise error
factory = AIProviderFactory()
print(factory.get_available_providers())  # ['openai', 'anthropic', 'local', 'mock']
```

---

### 2.3 OpenAI Provider Implementation

**File**: `app/ai_providers/openai_provider.py`

**Dependencies** (add to `requirements.txt`):
```
openai>=1.0.0
```

**Implementation**: See `03-ai-providers.md` for full code.

**Verification Test**:
```python
# Test OpenAI provider (requires API key)
import asyncio
from app.ai_providers.openai_provider import OpenAIProvider

async def test():
    provider = OpenAIProvider()
    response = await provider.generate_completion(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say hello in one word.",
        max_tokens=10
    )
    print(f"Response: {response}")

asyncio.run(test())
```

---

## 3. Phase 2: Core Module

### 3.1 Companion Schemas

**Create Directory**:
```bash
mkdir -p app/companion
```

**File**: `app/companion/schemas.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# ============ Settings Schemas ============

class CompanionSettings(BaseModel):
    """User's companion settings stored in user document"""
    opt_in_reflection_analysis: bool = False
    preferred_guidance_type: Literal["sankalpam", "breath-focus", "depth-focus", "none"] = "breath-focus"
    preferred_tts_voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova"
    preferred_ambient_sound: Literal["silence", "tibetan-bowl"] = "silence"
    default_meditation_duration: int = Field(default=10, ge=1, le=60)
    show_guidance_text: bool = True

class CompanionSettingsUpdate(BaseModel):
    """Partial update for companion settings"""
    opt_in_reflection_analysis: Optional[bool] = None
    preferred_guidance_type: Optional[Literal["sankalpam", "breath-focus", "depth-focus", "none"]] = None
    preferred_tts_voice: Optional[Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]] = None
    preferred_ambient_sound: Optional[Literal["silence", "tibetan-bowl"]] = None
    default_meditation_duration: Optional[int] = Field(default=None, ge=1, le=60)
    show_guidance_text: Optional[bool] = None

class CompanionSettingsResponse(CompanionSettings):
    """Response schema including timestamps"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ============ Reflection Prompt Schemas ============

class ReflectionPromptRequest(BaseModel):
    """Request for a personalized reflection prompt"""
    context: Optional[str] = Field(default=None, max_length=500)
    mood: Optional[Literal["peaceful", "contemplative", "seeking", "grateful"]] = None

class ReflectionPromptResponse(BaseModel):
    """Response containing the generated reflection prompt"""
    prompt: str
    based_on_reflections: bool
    reflection_themes: list[str] = []

# ============ Contemplative Question Schemas ============

class ContemplativeQuestionRequest(BaseModel):
    """Request for a contemplative question"""
    category: Optional[Literal["self", "relationships", "purpose", "presence", "gratitude"]] = None
    depth: Optional[Literal["gentle", "moderate", "deep"]] = "moderate"

class ContemplativeQuestionResponse(BaseModel):
    """Response containing the contemplative question"""
    question: str
    category: str
    follow_up_prompts: list[str] = []

# ============ Meditation Guidance Schemas ============

class MeditationGuidanceRequest(BaseModel):
    """Request for meditation guidance script"""
    duration_minutes: int = Field(ge=1, le=60)
    guidance_type: Literal["sankalpam", "breath-focus", "depth-focus"]
    include_intervals: bool = True
    interval_minutes: Optional[int] = Field(default=5, ge=1, le=30)

class MeditationGuidanceResponse(BaseModel):
    """Response containing meditation guidance"""
    opening: str
    settling: str
    intervals: list[str]
    closing: str
    total_duration: int  # in seconds

# ============ TTS Schemas ============

class TTSRequest(BaseModel):
    """Request for text-to-speech conversion"""
    text: str = Field(max_length=4096)
    voice: Optional[Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]] = None
```

---

### 3.2 Companion Repository

**File**: `app/companion/repository.py`

```python
from typing import Optional
from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.companion.schemas import CompanionSettings, CompanionSettingsUpdate

class CompanionRepository:
    """Repository for companion-related database operations"""

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
        # Ensure settings exist
        current = await self.get_settings(user_id)
        if not current:
            await self.create_default_settings(user_id)

        # Build update dict
        update_dict = update.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.get_settings(user_id)

        update_dict["updated_at"] = datetime.utcnow()

        # Update in database
        await self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {f"companion_settings.{k}": v for k, v in update_dict.items()}}
        )

        return await self.get_settings(user_id)

    async def get_user_opt_in_status(self, user_id: ObjectId) -> bool:
        """Check if user has opted in to reflection analysis"""
        user = await self.users_collection.find_one(
            {"_id": user_id},
            {"companion_settings.opt_in_reflection_analysis": 1}
        )

        if user and "companion_settings" in user:
            return user["companion_settings"].get("opt_in_reflection_analysis", False)
        return False
```

---

### 3.3 Prompt Templates

**Create Directory**:
```bash
mkdir -p app/companion/prompts
```

**Files**:
1. `app/companion/prompts/__init__.py`
2. `app/companion/prompts/system.py`
3. `app/companion/prompts/reflection.py`
4. `app/companion/prompts/contemplation.py`
5. `app/companion/prompts/meditation.py`
6. `app/companion/prompts/themes.py`
7. `app/companion/prompts/parsing.py`

**Implementation**: See `05-prompt-engineering.md` for full code.

---

### 3.4 Companion Service

**File**: `app/companion/service.py`

```python
from typing import Optional
from bson import ObjectId
import random

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
from app.companion.prompts import (
    COMPANION_SYSTEM_PROMPT,
    build_reflection_prompt,
    build_contemplation_prompt,
    build_meditation_prompt,
    FALLBACK_REFLECTION_PROMPTS,
    FALLBACK_QUESTIONS,
    FALLBACK_MEDITATION
)
from app.companion.prompts.themes import extract_themes, summarize_for_context
from app.companion.prompts.parsing import parse_question_response, parse_meditation_response, clean_response
from app.ai_providers.base import AIProvider, AIProviderError
from app.posts.repository import PostRepository

class CompanionService:
    """Service for AI companion features"""

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
        """Get user's companion settings"""
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
                limit=10
            )
            if recent_posts:
                user_context = summarize_for_context(recent_posts)
                all_text = " ".join(p.get("content", "") for p in recent_posts)
                reflection_themes = extract_themes(all_text)

        try:
            # Build and send prompt to AI
            ai_prompt = build_reflection_prompt(
                user_context=user_context,
                mood=request.mood,
                additional_context=request.context
            )

            response = await self.ai_provider.generate_completion(
                system_prompt=COMPANION_SYSTEM_PROMPT,
                user_prompt=ai_prompt,
                max_tokens=300,
                temperature=0.8
            )

            return ReflectionPromptResponse(
                prompt=clean_response(response),
                based_on_reflections=user_context is not None,
                reflection_themes=reflection_themes
            )

        except AIProviderError as e:
            # Return fallback prompt
            return ReflectionPromptResponse(
                prompt=random.choice(FALLBACK_REFLECTION_PROMPTS),
                based_on_reflections=False,
                reflection_themes=[]
            )

    async def generate_contemplative_question(
        self,
        user_id: ObjectId,
        request: ContemplativeQuestionRequest
    ) -> ContemplativeQuestionResponse:
        """Generate a contemplative question"""
        settings = await self.get_settings(user_id)

        # Get context if opted in
        user_context = None
        if settings.opt_in_reflection_analysis:
            recent_posts = await self.post_repository.get_user_posts(
                user_id=user_id,
                limit=5
            )
            if recent_posts:
                user_context = summarize_for_context(recent_posts, max_chars=1000)

        try:
            ai_prompt = build_contemplation_prompt(
                category=request.category,
                depth=request.depth,
                user_context=user_context
            )

            response = await self.ai_provider.generate_completion(
                system_prompt=COMPANION_SYSTEM_PROMPT,
                user_prompt=ai_prompt,
                max_tokens=400,
                temperature=0.8
            )

            parsed = parse_question_response(response)
            category = request.category or "general"

            return ContemplativeQuestionResponse(
                question=parsed["question"],
                category=category,
                follow_up_prompts=parsed.get("follow_ups", [])
            )

        except AIProviderError:
            # Return fallback question
            category = request.category or "presence"
            fallback = random.choice(FALLBACK_QUESTIONS.get(category, FALLBACK_QUESTIONS["presence"]))

            return ContemplativeQuestionResponse(
                question=fallback,
                category=category,
                follow_up_prompts=[]
            )

    async def generate_meditation_guidance(
        self,
        user_id: ObjectId,
        request: MeditationGuidanceRequest
    ) -> MeditationGuidanceResponse:
        """Generate meditation guidance script"""

        # Calculate intervals
        num_intervals = 0
        if request.include_intervals and request.interval_minutes:
            num_intervals = (request.duration_minutes // request.interval_minutes) - 1
            num_intervals = max(0, min(num_intervals, 10))

        try:
            ai_prompt = build_meditation_prompt(
                guidance_type=request.guidance_type,
                duration_minutes=request.duration_minutes,
                num_intervals=num_intervals
            )

            response = await self.ai_provider.generate_completion(
                system_prompt=COMPANION_SYSTEM_PROMPT,
                user_prompt=ai_prompt,
                max_tokens=1500,
                temperature=0.7
            )

            parsed = parse_meditation_response(response)

            return MeditationGuidanceResponse(
                opening=parsed["opening"],
                settling=parsed["settling"],
                intervals=parsed["intervals"][:num_intervals] if num_intervals > 0 else [],
                closing=parsed["closing"],
                total_duration=request.duration_minutes * 60
            )

        except AIProviderError:
            # Return fallback guidance
            fallback = FALLBACK_MEDITATION.get(
                request.guidance_type,
                FALLBACK_MEDITATION["breath-focus"]
            )

            return MeditationGuidanceResponse(
                opening=fallback["opening"],
                settling=fallback["settling"],
                intervals=fallback["intervals"][:num_intervals] if num_intervals > 0 else [],
                closing=fallback["closing"],
                total_duration=request.duration_minutes * 60
            )

    async def generate_tts(self, text: str, voice: str) -> bytes:
        """Generate text-to-speech audio"""
        return await self.ai_provider.generate_tts(text=text, voice=voice)
```

---

## 4. Phase 3: API Layer

### 4.1 Companion Router

**File**: `app/companion/router.py`

```python
from fastapi import APIRouter, Depends, Response, HTTPException
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
from app.ai_providers.base import AIProviderError

router = APIRouter(prefix="/api/companion", tags=["companion"])


@router.get("/settings")
async def get_settings(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Get user's companion settings"""
    settings = await service.get_settings(current_user["_id"])
    return format_response(settings.model_dump())


@router.put("/settings")
async def update_settings(
    settings_update: CompanionSettingsUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Update user's companion settings"""
    settings = await service.update_settings(current_user["_id"], settings_update)
    return format_response(settings.model_dump())


@router.post("/prompt")
async def get_reflection_prompt(
    request: ReflectionPromptRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Get a personalized reflection prompt"""
    result = await service.generate_reflection_prompt(current_user["_id"], request)
    return format_response(result.model_dump())


@router.post("/question")
async def get_contemplative_question(
    request: ContemplativeQuestionRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Get a contemplative question"""
    result = await service.generate_contemplative_question(current_user["_id"], request)
    return format_response(result.model_dump())


@router.post("/meditation")
async def get_meditation_guidance(
    request: MeditationGuidanceRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Get meditation guidance script"""
    result = await service.generate_meditation_guidance(current_user["_id"], request)
    return format_response(result.model_dump())


@router.post("/tts")
async def text_to_speech(
    request: TTSRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[CompanionService, Depends(get_companion_service)]
):
    """Convert text to speech audio"""
    try:
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
                "Content-Disposition": "inline; filename=guidance.mp3",
                "Cache-Control": "no-cache"
            }
        )

    except AIProviderError as e:
        raise HTTPException(status_code=503, detail=f"TTS generation failed: {e.message}")
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
```

---

### 4.2 Dependencies

**File**: `app/companion/dependencies.py`

```python
from fastapi import Depends
from typing import Annotated

from app.database.connection import get_database
from app.companion.repository import CompanionRepository
from app.companion.service import CompanionService
from app.posts.repository import PostRepository
from app.ai_providers import get_ai_provider
from app.ai_providers.base import AIProvider


async def get_companion_repository(
    db=Depends(get_database)
) -> CompanionRepository:
    """Get companion repository instance"""
    return CompanionRepository(db)


async def get_post_repository(
    db=Depends(get_database)
) -> PostRepository:
    """Get post repository instance"""
    return PostRepository(db)


async def get_companion_service(
    repository: Annotated[CompanionRepository, Depends(get_companion_repository)],
    post_repository: Annotated[PostRepository, Depends(get_post_repository)],
    ai_provider: Annotated[AIProvider, Depends(get_ai_provider)]
) -> CompanionService:
    """Get companion service instance with dependencies"""
    return CompanionService(
        repository=repository,
        post_repository=post_repository,
        ai_provider=ai_provider
    )
```

---

### 4.3 Main App Registration

**File**: `app/main.py` (add to existing)

```python
# Add import
from app.companion.router import router as companion_router

# Add to router registration (after existing routers)
app.include_router(companion_router)
```

---

## 5. Phase 4: Polish

### 5.1 Error Handling

**File**: `app/companion/exceptions.py`

```python
from fastapi import HTTPException

class CompanionException(HTTPException):
    """Base exception for companion module"""
    pass

class AIUnavailableException(CompanionException):
    def __init__(self):
        super().__init__(
            status_code=503,
            detail="AI service temporarily unavailable. Please try again."
        )

class TTSException(CompanionException):
    def __init__(self, message: str = "Text-to-speech generation failed"):
        super().__init__(status_code=500, detail=message)

class RateLimitException(CompanionException):
    def __init__(self):
        super().__init__(
            status_code=429,
            detail="Too many requests. Please wait before trying again."
        )
```

---

### 5.2 Rate Limiting

**File**: `app/companion/rate_limiter.py`

```python
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

from app.config.settings import settings

class CompanionRateLimiter:
    """Simple in-memory rate limiter for companion endpoints"""

    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        limit: int,
        window_seconds: int
    ) -> bool:
        """
        Check if request is within rate limit.

        Returns True if allowed, raises HTTPException if exceeded.
        """
        async with self.lock:
            key = f"{user_id}:{endpoint}"
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window_seconds)

            # Clean old requests
            self.requests[key] = [
                ts for ts in self.requests[key]
                if ts > window_start
            ]

            # Check limit
            if len(self.requests[key]) >= limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {limit} requests per {window_seconds // 60} minutes."
                )

            # Record this request
            self.requests[key].append(now)
            return True


# Global rate limiter instance
rate_limiter = CompanionRateLimiter()


# Dependency functions
async def check_prompt_rate_limit(request: Request):
    user_id = str(request.state.user["_id"])
    await rate_limiter.check_rate_limit(
        user_id, "prompt",
        settings.COMPANION_RATE_LIMIT_PROMPT,
        settings.COMPANION_RATE_LIMIT_WINDOW
    )

async def check_question_rate_limit(request: Request):
    user_id = str(request.state.user["_id"])
    await rate_limiter.check_rate_limit(
        user_id, "question",
        settings.COMPANION_RATE_LIMIT_QUESTION,
        settings.COMPANION_RATE_LIMIT_WINDOW
    )

async def check_meditation_rate_limit(request: Request):
    user_id = str(request.state.user["_id"])
    await rate_limiter.check_rate_limit(
        user_id, "meditation",
        settings.COMPANION_RATE_LIMIT_MEDITATION,
        settings.COMPANION_RATE_LIMIT_WINDOW
    )

async def check_tts_rate_limit(request: Request):
    user_id = str(request.state.user["_id"])
    await rate_limiter.check_rate_limit(
        user_id, "tts",
        settings.COMPANION_RATE_LIMIT_TTS,
        settings.COMPANION_RATE_LIMIT_WINDOW
    )
```

---

### 5.3 Module Init Files

**File**: `app/companion/__init__.py`

```python
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
    TTSRequest
)

__all__ = [
    "router",
    "CompanionService",
    "CompanionSettings",
    "CompanionSettingsUpdate",
    "ReflectionPromptRequest",
    "ReflectionPromptResponse",
    "ContemplativeQuestionRequest",
    "ContemplativeQuestionResponse",
    "MeditationGuidanceRequest",
    "MeditationGuidanceResponse",
    "TTSRequest"
]
```

---

## 6. File Checklist

### New Files to Create

```
app/
├── ai_providers/
│   ├── __init__.py              ☐
│   ├── base.py                  ☐
│   ├── openai_provider.py       ☐
│   ├── anthropic_provider.py    ☐
│   ├── local_provider.py        ☐
│   ├── mock_provider.py         ☐
│   ├── factory.py               ☐
│   └── config.py                ☐
│
├── companion/
│   ├── __init__.py              ☐
│   ├── router.py                ☐
│   ├── service.py               ☐
│   ├── repository.py            ☐
│   ├── schemas.py               ☐
│   ├── dependencies.py          ☐
│   ├── constants.py             ☐
│   ├── exceptions.py            ☐
│   ├── rate_limiter.py          ☐
│   └── prompts/
│       ├── __init__.py          ☐
│       ├── system.py            ☐
│       ├── reflection.py        ☐
│       ├── contemplation.py     ☐
│       ├── meditation.py        ☐
│       ├── themes.py            ☐
│       └── parsing.py           ☐
```

### Files to Modify

```
app/
├── config/
│   └── settings.py              ☐ (add AI provider settings)
│
├── main.py                      ☐ (register companion router)
│
└── posts/
    └── repository.py            ☐ (ensure get_user_posts method exists)
```

### Dependencies to Add

```
requirements.txt:
├── openai>=1.0.0                ☐
└── anthropic>=0.18.0            ☐ (optional)
```

---

## 7. Testing Commands

```bash
# Install dependencies
pip install openai anthropic

# Run backend
uvicorn app.main:app --reload

# Test endpoints (with httpie or curl)
# Get settings
http GET localhost:8000/api/companion/settings "Authorization: Bearer $TOKEN"

# Update settings (opt-in)
http PUT localhost:8000/api/companion/settings "Authorization: Bearer $TOKEN" opt_in_reflection_analysis:=true

# Get reflection prompt
http POST localhost:8000/api/companion/prompt "Authorization: Bearer $TOKEN"

# Get question
http POST localhost:8000/api/companion/question "Authorization: Bearer $TOKEN" category=self depth=moderate

# Get meditation guidance
http POST localhost:8000/api/companion/meditation "Authorization: Bearer $TOKEN" duration_minutes:=10 guidance_type=breath-focus

# Test TTS (saves audio file)
http POST localhost:8000/api/companion/tts "Authorization: Bearer $TOKEN" text="Welcome to this moment." > test.mp3
```
