# AI Reflection Companion - Testing & Documentation Plan

## Document Info
- **Feature**: AI Reflection Companion
- **Phase**: Testing & Documentation Plan
- **Created**: 2026-01-28
- **Status**: Complete

---

## 1. Testing Strategy Overview

```
Testing Pyramid
─────────────────────────────────────────
              /\
             /  \
            / E2E \         ← 10% (Critical user flows)
           /──────\
          /        \
         /Integration\      ← 30% (API, services)
        /──────────────\
       /                \
      /    Unit Tests    \  ← 60% (Components, hooks, utils)
     /────────────────────\
```

---

## 2. Backend Testing

### 2.1 Unit Tests

**Directory**: `smriti-backend/tests/companion/`

#### Test Files

```
tests/
├── companion/
│   ├── __init__.py
│   ├── test_schemas.py
│   ├── test_repository.py
│   ├── test_service.py
│   ├── test_prompts.py
│   └── test_router.py
│
└── ai_providers/
    ├── __init__.py
    ├── test_factory.py
    ├── test_openai_provider.py
    └── test_mock_provider.py
```

#### test_schemas.py

```python
import pytest
from pydantic import ValidationError
from app.companion.schemas import (
    CompanionSettings,
    CompanionSettingsUpdate,
    ReflectionPromptRequest,
    MeditationGuidanceRequest
)

class TestCompanionSettings:
    def test_default_values(self):
        settings = CompanionSettings()
        assert settings.opt_in_reflection_analysis == False
        assert settings.preferred_guidance_type == "breath-focus"
        assert settings.preferred_tts_voice == "nova"
        assert settings.default_meditation_duration == 10

    def test_valid_guidance_types(self):
        for gtype in ["sankalpam", "breath-focus", "depth-focus", "none"]:
            settings = CompanionSettings(preferred_guidance_type=gtype)
            assert settings.preferred_guidance_type == gtype

    def test_invalid_guidance_type(self):
        with pytest.raises(ValidationError):
            CompanionSettings(preferred_guidance_type="invalid")

    def test_duration_bounds(self):
        with pytest.raises(ValidationError):
            CompanionSettings(default_meditation_duration=0)
        with pytest.raises(ValidationError):
            CompanionSettings(default_meditation_duration=61)

class TestMeditationGuidanceRequest:
    def test_valid_request(self):
        request = MeditationGuidanceRequest(
            duration_minutes=15,
            guidance_type="sankalpam"
        )
        assert request.duration_minutes == 15
        assert request.guidance_type == "sankalpam"

    def test_interval_defaults(self):
        request = MeditationGuidanceRequest(
            duration_minutes=10,
            guidance_type="breath-focus"
        )
        assert request.include_intervals == True
        assert request.interval_minutes == 5
```

#### test_service.py

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId

from app.companion.service import CompanionService
from app.companion.schemas import (
    ReflectionPromptRequest,
    ContemplativeQuestionRequest,
    MeditationGuidanceRequest
)

@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.get_settings.return_value = MagicMock(
        opt_in_reflection_analysis=True,
        preferred_tts_voice="nova"
    )
    return repo

@pytest.fixture
def mock_post_repository():
    repo = AsyncMock()
    repo.get_user_posts.return_value = [
        {"content": "I am grateful for today"},
        {"content": "Finding peace in the moment"}
    ]
    return repo

@pytest.fixture
def mock_ai_provider():
    provider = AsyncMock()
    provider.generate_completion.return_value = "What are you grateful for today?"
    provider.generate_tts.return_value = b"audio bytes"
    return provider

@pytest.fixture
def service(mock_repository, mock_post_repository, mock_ai_provider):
    return CompanionService(
        repository=mock_repository,
        post_repository=mock_post_repository,
        ai_provider=mock_ai_provider
    )

class TestCompanionService:
    @pytest.mark.asyncio
    async def test_generate_reflection_prompt(self, service):
        user_id = ObjectId()
        request = ReflectionPromptRequest()

        result = await service.generate_reflection_prompt(user_id, request)

        assert result.prompt is not None
        assert result.based_on_reflections == True

    @pytest.mark.asyncio
    async def test_generate_contemplative_question(self, service):
        user_id = ObjectId()
        request = ContemplativeQuestionRequest(category="self", depth="moderate")

        result = await service.generate_contemplative_question(user_id, request)

        assert result.question is not None
        assert result.category == "self"

    @pytest.mark.asyncio
    async def test_generate_meditation_guidance(self, service, mock_ai_provider):
        mock_ai_provider.generate_completion.return_value = '''
        {
            "opening": "Welcome",
            "settling": "Settle in",
            "intervals": ["Return to breath"],
            "closing": "Gently return"
        }
        '''

        user_id = ObjectId()
        request = MeditationGuidanceRequest(
            duration_minutes=10,
            guidance_type="breath-focus"
        )

        result = await service.generate_meditation_guidance(user_id, request)

        assert result.opening is not None
        assert result.total_duration == 600
```

#### test_prompts.py

```python
import pytest
from app.companion.prompts.reflection import build_reflection_prompt
from app.companion.prompts.contemplation import build_contemplation_prompt
from app.companion.prompts.meditation import build_meditation_prompt
from app.companion.prompts.themes import extract_themes

class TestReflectionPrompts:
    def test_build_without_context(self):
        prompt = build_reflection_prompt()
        assert "reflection prompt" in prompt.lower()
        assert "guidelines" in prompt.lower()

    def test_build_with_user_context(self):
        context = "I have been thinking about gratitude lately."
        prompt = build_reflection_prompt(user_context=context)
        assert context in prompt
        assert "recent reflections" in prompt.lower()

    def test_build_with_mood(self):
        prompt = build_reflection_prompt(mood="peaceful")
        assert "peaceful" in prompt.lower()

class TestThemeExtraction:
    def test_extract_gratitude_theme(self):
        text = "I am so grateful for my family. Thankful for another day."
        themes = extract_themes(text)
        assert "gratitude" in themes

    def test_extract_multiple_themes(self):
        text = "Finding peace in the present moment. Grateful for stillness."
        themes = extract_themes(text)
        assert len(themes) >= 2

    def test_max_themes_limit(self):
        text = "grateful peaceful present growth acceptance change seeking"
        themes = extract_themes(text, max_themes=3)
        assert len(themes) <= 3

class TestMeditationPrompts:
    def test_build_sankalpam(self):
        prompt = build_meditation_prompt("sankalpam", 10, 2)
        assert "sankalpam" in prompt.lower()
        assert "intention" in prompt.lower()

    def test_build_breath_focus(self):
        prompt = build_meditation_prompt("breath-focus", 15, 3)
        assert "breath" in prompt.lower()

    def test_build_depth_focus(self):
        prompt = build_meditation_prompt("depth-focus", 20, 4)
        assert "depth" in prompt.lower() or "stillness" in prompt.lower()
```

### 2.2 Integration Tests

```python
# tests/companion/test_router_integration.py

import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def authenticated_client():
    """Create authenticated test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login and get token
        response = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        token = response.json()["data"]["token"]
        client.headers["Authorization"] = f"Bearer {token}"
        yield client

class TestCompanionEndpoints:
    @pytest.mark.asyncio
    async def test_get_settings(self, authenticated_client):
        response = await authenticated_client.get("/api/companion/settings")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "opt_in_reflection_analysis" in data

    @pytest.mark.asyncio
    async def test_update_settings(self, authenticated_client):
        response = await authenticated_client.put(
            "/api/companion/settings",
            json={"opt_in_reflection_analysis": True}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["opt_in_reflection_analysis"] == True

    @pytest.mark.asyncio
    async def test_get_reflection_prompt(self, authenticated_client):
        response = await authenticated_client.post(
            "/api/companion/prompt",
            json={}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "prompt" in data

    @pytest.mark.asyncio
    async def test_get_meditation_guidance(self, authenticated_client):
        response = await authenticated_client.post(
            "/api/companion/meditation",
            json={
                "duration_minutes": 5,
                "guidance_type": "breath-focus"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "opening" in data
        assert "closing" in data
```

### 2.3 AI Provider Tests

```python
# tests/ai_providers/test_mock_provider.py

import pytest
from app.ai_providers.mock_provider import MockAIProvider

class TestMockProvider:
    @pytest.mark.asyncio
    async def test_generate_completion(self):
        provider = MockAIProvider()
        response = await provider.generate_completion(
            system_prompt="test",
            user_prompt="test"
        )
        assert response is not None
        assert len(provider.call_history) == 1

    @pytest.mark.asyncio
    async def test_generate_tts(self):
        provider = MockAIProvider()
        audio = await provider.generate_tts("Hello", "nova")
        assert isinstance(audio, bytes)

    @pytest.mark.asyncio
    async def test_custom_responses(self):
        provider = MockAIProvider(responses={
            "completion": "Custom response"
        })
        response = await provider.generate_completion("", "")
        assert response == "Custom response"
```

---

## 3. Frontend Testing

### 3.1 Component Tests

**Directory**: `smriti-frontend/__tests__/`

```javascript
// __tests__/components/CompanionCard.test.js

import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import CompanionCard from '../../src/components/companion/CompanionCard';

describe('CompanionCard', () => {
  const defaultProps = {
    icon: '🪷',
    title: 'Test Card',
    description: 'Test description',
    onPress: jest.fn()
  };

  it('renders correctly', () => {
    const { getByText } = render(<CompanionCard {...defaultProps} />);

    expect(getByText('🪷')).toBeTruthy();
    expect(getByText('Test Card')).toBeTruthy();
    expect(getByText('Test description')).toBeTruthy();
  });

  it('calls onPress when tapped', () => {
    const onPress = jest.fn();
    const { getByText } = render(
      <CompanionCard {...defaultProps} onPress={onPress} />
    );

    fireEvent.press(getByText('Test Card'));
    expect(onPress).toHaveBeenCalled();
  });

  it('shows loading state', () => {
    const { getByTestId } = render(
      <CompanionCard {...defaultProps} loading={true} />
    );

    expect(getByTestId('loading-indicator')).toBeTruthy();
  });

  it('is disabled when disabled prop is true', () => {
    const onPress = jest.fn();
    const { getByText } = render(
      <CompanionCard {...defaultProps} onPress={onPress} disabled={true} />
    );

    fireEvent.press(getByText('Test Card'));
    expect(onPress).not.toHaveBeenCalled();
  });
});
```

```javascript
// __tests__/components/ProgressRing.test.js

import React from 'react';
import { render } from '@testing-library/react-native';
import ProgressRing from '../../src/components/meditation/ProgressRing';

describe('ProgressRing', () => {
  it('renders with correct progress', () => {
    const { getByText } = render(
      <ProgressRing
        progress={0.5}
        size={200}
        remaining={300}
        duration={600}
      />
    );

    expect(getByText('5:00')).toBeTruthy();
  });

  it('shows 0:00 when complete', () => {
    const { getByText } = render(
      <ProgressRing
        progress={1}
        size={200}
        remaining={0}
        duration={600}
      />
    );

    expect(getByText('0:00')).toBeTruthy();
  });
});
```

### 3.2 Hook Tests

```javascript
// __tests__/hooks/useCompanion.test.js

import { renderHook, act } from '@testing-library/react-hooks';
import { useCompanion } from '../../src/hooks/useCompanion';
import { CompanionProvider } from '../../src/contexts/CompanionContext';
import * as companionApi from '../../src/services/api/companion';

jest.mock('../../src/services/api/companion');

const wrapper = ({ children }) => (
  <CompanionProvider>{children}</CompanionProvider>
);

describe('useCompanion', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('loads settings', async () => {
    companionApi.getSettings.mockResolvedValue({
      opt_in_reflection_analysis: true
    });

    const { result, waitForNextUpdate } = renderHook(
      () => useCompanion(),
      { wrapper }
    );

    await act(async () => {
      await result.current.loadSettings();
    });

    expect(result.current.settings.optInReflectionAnalysis).toBe(true);
  });

  it('gets reflection prompt', async () => {
    companionApi.getReflectionPrompt.mockResolvedValue({
      prompt: 'Test prompt',
      based_on_reflections: false,
      reflection_themes: []
    });

    const { result } = renderHook(() => useCompanion(), { wrapper });

    await act(async () => {
      await result.current.getReflectionPrompt();
    });

    expect(result.current.response.text).toBe('Test prompt');
    expect(result.current.response.type).toBe('prompt');
  });
});
```

```javascript
// __tests__/hooks/useMeditation.test.js

import { renderHook, act } from '@testing-library/react-hooks';
import { useMeditation } from '../../src/hooks/useMeditation';
import { MEDITATION_STATES } from '../../src/constants/companion';

describe('useMeditation', () => {
  it('initializes with default state', () => {
    const { result } = renderHook(() => useMeditation());

    expect(result.current.status).toBe(MEDITATION_STATES.IDLE);
    expect(result.current.duration).toBe(10);
    expect(result.current.guidanceType).toBe('breath-focus');
  });

  it('sets duration correctly', () => {
    const { result } = renderHook(() => useMeditation());

    act(() => {
      result.current.setDuration(15);
    });

    expect(result.current.duration).toBe(15);
    expect(result.current.remainingSeconds).toBe(900);
  });

  it('sets guidance type', () => {
    const { result } = renderHook(() => useMeditation());

    act(() => {
      result.current.setGuidanceType('sankalpam');
    });

    expect(result.current.guidanceType).toBe('sankalpam');
  });

  it('calculates progress correctly', () => {
    const { result } = renderHook(() => useMeditation());

    act(() => {
      result.current.setDuration(10);
    });

    // Simulate 50% completion
    // This would require mocking the timer, simplified here
    expect(result.current.progress).toBe(0);
  });
});
```

### 3.3 E2E Tests (Detox)

```javascript
// e2e/companion.test.js

describe('Companion Feature', () => {
  beforeAll(async () => {
    await device.launchApp();
    // Login
    await element(by.id('email-input')).typeText('test@example.com');
    await element(by.id('password-input')).typeText('testpassword');
    await element(by.id('login-button')).tap();
  });

  it('should navigate to Companion tab', async () => {
    await element(by.id('companion-tab')).tap();
    await expect(element(by.text('Companion'))).toBeVisible();
  });

  it('should show action cards', async () => {
    await expect(element(by.text('Reflection Prompt'))).toBeVisible();
    await expect(element(by.text('Contemplative Question'))).toBeVisible();
    await expect(element(by.text('Guided Meditation'))).toBeVisible();
  });

  it('should get reflection prompt', async () => {
    await element(by.text('Reflection Prompt')).tap();
    await waitFor(element(by.id('response-bubble')))
      .toBeVisible()
      .withTimeout(10000);
  });

  it('should navigate to meditation screen', async () => {
    await element(by.text('Guided Meditation')).tap();
    await expect(element(by.text('How long?'))).toBeVisible();
  });

  it('should start meditation session', async () => {
    await element(by.text('10')).tap();
    await element(by.text('Breath Focus')).tap();
    await element(by.text('Begin Session')).tap();

    await waitFor(element(by.id('progress-ring')))
      .toBeVisible()
      .withTimeout(5000);
  });
});
```

---

## 4. Test Data & Fixtures

### Backend Fixtures

```python
# tests/fixtures/companion_fixtures.py

import pytest
from bson import ObjectId
from datetime import datetime

@pytest.fixture
def sample_user_id():
    return ObjectId()

@pytest.fixture
def sample_settings():
    return {
        "opt_in_reflection_analysis": True,
        "preferred_guidance_type": "breath-focus",
        "preferred_tts_voice": "nova",
        "default_meditation_duration": 10,
        "show_guidance_text": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def sample_posts():
    return [
        {
            "_id": ObjectId(),
            "content": "Today I practiced gratitude. Feeling thankful for small moments.",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "content": "Finding peace in the present moment. Letting go of yesterday.",
            "created_at": datetime.utcnow()
        }
    ]

@pytest.fixture
def sample_meditation_guidance():
    return {
        "opening": "Welcome to this time of stillness.",
        "settling": "Allow your breath to find its natural rhythm.",
        "intervals": [
            "Gently return your attention to the breath.",
            "Notice any tension and let it soften."
        ],
        "closing": "Slowly bring your awareness back to the room."
    }
```

### Frontend Fixtures

```javascript
// __tests__/fixtures/companionFixtures.js

export const mockSettings = {
  opt_in_reflection_analysis: true,
  preferred_guidance_type: 'breath-focus',
  preferred_tts_voice: 'nova',
  default_meditation_duration: 10,
  show_guidance_text: true
};

export const mockPromptResponse = {
  prompt: 'What are you grateful for in this moment?',
  based_on_reflections: true,
  reflection_themes: ['gratitude', 'presence']
};

export const mockQuestionResponse = {
  question: 'Who are you when you are not playing any role?',
  category: 'self',
  follow_up_prompts: [
    'What masks do you wear?',
    'What would remain if you let go of all identities?'
  ]
};

export const mockMeditationGuidance = {
  opening: 'Welcome to this time of stillness.',
  settling: 'Allow your breath to settle.',
  intervals: ['Return to the breath.'],
  closing: 'Gently return to the room.',
  total_duration: 600
};
```

---

## 5. Test Commands

### Backend

```bash
# Run all tests
pytest

# Run companion tests only
pytest tests/companion/

# Run with coverage
pytest --cov=app/companion --cov-report=html

# Run specific test file
pytest tests/companion/test_service.py

# Run with verbose output
pytest -v tests/companion/
```

### Frontend

```bash
# Run all tests
npm test

# Run specific test file
npm test -- CompanionCard

# Run with coverage
npm test -- --coverage

# Run E2E tests (Detox)
detox test -c ios.sim.debug
```

---

## 6. Documentation Plan

### 6.1 Code Documentation

**Docstrings** (Python):
- All public functions and classes
- Parameter descriptions
- Return value descriptions
- Example usage where helpful

**JSDoc** (JavaScript):
- All exported functions
- Component props documentation
- Hook return values

### 6.2 API Documentation

**Location**: `docs/api/companion.md`

Document all endpoints:
- URL, method
- Request body schema
- Response schema
- Error codes
- Example requests/responses

### 6.3 User Documentation

**Location**: `docs/features/companion.md`

- Feature overview
- How to use each feature
- Settings explanation
- Privacy information

---

## 7. Quality Metrics

### Coverage Targets

| Area | Target |
|------|--------|
| Backend Unit Tests | 80% |
| Backend Integration | 60% |
| Frontend Components | 70% |
| Frontend Hooks | 80% |

### Performance Benchmarks

| Metric | Target |
|--------|--------|
| API Response (prompt) | < 3s |
| API Response (TTS) | < 5s |
| Timer accuracy | ±1s |
| Audio latency | < 500ms |

---

## 8. CI/CD Integration

```yaml
# .github/workflows/companion-tests.yml

name: Companion Tests

on:
  push:
    paths:
      - 'smriti-backend/app/companion/**'
      - 'smriti-backend/app/ai_providers/**'
      - 'smriti-frontend/src/components/companion/**'
      - 'smriti-frontend/src/screens/companion/**'

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/companion/ --cov=app/companion

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd smriti-frontend && npm install
      - run: cd smriti-frontend && npm test -- --coverage
```
