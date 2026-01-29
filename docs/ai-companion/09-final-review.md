# AI Reflection Companion - Final Review & Refinements

## Document Info
- **Feature**: AI Reflection Companion
- **Phase**: Final Review
- **Created**: 2026-01-28
- **Status**: Complete

---

## 1. Feature Summary

The AI Reflection Companion is a thoughtful, spiritual AI assistant for Smriti that helps users deepen their reflection and meditation practice.

### Core Capabilities Delivered

| Capability | Status | Notes |
|------------|--------|-------|
| Personalized Reflection Prompts | ✅ Designed | Based on user's past reflections (opt-in) |
| Contemplative Questions | ✅ Designed | 5 categories, 3 depth levels |
| Guided Meditation | ✅ Designed | Sankalpam, Breath Focus, Depth Focus |
| TTS Voice Guidance | ✅ Designed | OpenAI TTS with "nova" voice |
| Timer with Progress Ring | ✅ Designed | Visual countdown, interval bells |
| Tibetan Bowl Bells | ✅ Designed | Start/end session bells |
| Settings & Opt-in | ✅ Designed | User controls, privacy-first |
| AI Provider Abstraction | ✅ Designed | OpenAI, Anthropic, Local, Mock |

---

## 2. Architecture Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| AI Provider | OpenAI (primary) | User preference, TTS support |
| Provider Pattern | Abstract Factory | Easy switching between providers |
| TTS Voice | nova | Calm, warm tone for meditation |
| Meditation Types | Sankalpam, Breath Focus, Depth Focus | User-specified spiritual practices |
| Audio | Silence + Tibetan Bowl | Minimal, user preference |
| Conversation Storage | Ephemeral | Privacy, "letting go" philosophy |
| UI Placement | 5th bottom tab | Most accessible |
| Reflection Analysis | Server-side, opt-in | Privacy-first approach |

---

## 3. Documentation Index

| # | Document | Description | Status |
|---|----------|-------------|--------|
| 00 | [00-overview.md](./00-overview.md) | Feature overview & requirements | ✅ |
| 01 | [01-architecture.md](./01-architecture.md) | System architecture design | ✅ |
| 02 | [02-backend-api.md](./02-backend-api.md) | Backend schema & API design | ✅ |
| 03 | [03-ai-providers.md](./03-ai-providers.md) | AI provider abstraction design | ✅ |
| 04 | [04-frontend-components.md](./04-frontend-components.md) | Frontend component design | ✅ |
| 05 | [05-prompt-engineering.md](./05-prompt-engineering.md) | Prompt templates design | ✅ |
| 06 | [06-implementation-backend.md](./06-implementation-backend.md) | Backend implementation plan | ✅ |
| 07 | [07-implementation-frontend.md](./07-implementation-frontend.md) | Frontend implementation plan | ✅ |
| 08 | [08-testing.md](./08-testing.md) | Testing & documentation plan | ✅ |
| 09 | [09-final-review.md](./09-final-review.md) | This document | ✅ |

---

## 4. Implementation Checklist

### Backend (Phase 1)

```
☐ Add AI provider settings to config/settings.py
☐ Create app/ai_providers/ module
  ☐ base.py (abstract class)
  ☐ openai_provider.py
  ☐ anthropic_provider.py
  ☐ local_provider.py
  ☐ mock_provider.py
  ☐ factory.py
  ☐ config.py
  ☐ __init__.py
☐ Install dependencies (openai, anthropic)
☐ Test AI provider factory
```

### Backend (Phase 2)

```
☐ Create app/companion/ module
  ☐ schemas.py
  ☐ repository.py
  ☐ prompts/
    ☐ system.py
    ☐ reflection.py
    ☐ contemplation.py
    ☐ meditation.py
    ☐ themes.py
    ☐ parsing.py
  ☐ service.py
  ☐ router.py
  ☐ dependencies.py
  ☐ __init__.py
☐ Register router in main.py
☐ Test all endpoints
```

### Frontend (Phase 1)

```
☐ Install dependencies (expo-av, expo-keep-awake)
☐ Add constants/companion.js
☐ Add services/api/companion.js
☐ Add services/audioService.js
☐ Add audio assets (tibetan-bowl.mp3)
```

### Frontend (Phase 2)

```
☐ Create contexts/CompanionContext.js
☐ Create hooks/useCompanion.js
☐ Create hooks/useMeditation.js
```

### Frontend (Phase 3)

```
☐ Create components/companion/
  ☐ CompanionCard.js
  ☐ ResponseBubble.js
  ☐ OptInBanner.js
  ☐ TTSButton.js
☐ Create components/meditation/
  ☐ DurationPicker.js
  ☐ GuidanceTypePicker.js
  ☐ ProgressRing.js
  ☐ TimerDisplay.js
  ☐ GuidanceDisplay.js
  ☐ TimerControls.js
```

### Frontend (Phase 4)

```
☐ Create screens/companion/
  ☐ CompanionScreen.js
  ☐ MeditationScreen.js
  ☐ CompanionSettingsScreen.js
☐ Create navigation/CompanionStackNavigator.js
☐ Update navigation/AppNavigator.js (add 5th tab)
☐ Update App.js (add CompanionProvider)
☐ Update app.json (background audio)
```

### Testing

```
☐ Backend unit tests
☐ Backend integration tests
☐ Frontend component tests
☐ Frontend hook tests
☐ Manual testing
```

---

## 5. Environment Variables Required

```bash
# .env (Backend)

# Required
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# Optional (for switching providers)
OPENAI_MODEL=gpt-4o-mini
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=nova
ANTHROPIC_API_KEY=
LOCAL_MODEL_URL=http://localhost:11434
LOCAL_MODEL_NAME=llama3

# Rate limits
COMPANION_RATE_LIMIT_PROMPT=20
COMPANION_RATE_LIMIT_QUESTION=20
COMPANION_RATE_LIMIT_MEDITATION=10
COMPANION_RATE_LIMIT_TTS=30
COMPANION_RATE_LIMIT_WINDOW=3600
```

---

## 6. Dependencies to Add

### Backend (requirements.txt)

```
openai>=1.0.0
anthropic>=0.18.0  # optional
httpx>=0.25.0      # for local models
```

### Frontend (package.json)

```json
{
  "dependencies": {
    "expo-av": "~14.0.0",
    "expo-keep-awake": "~13.0.0",
    "react-native-svg": "latest"
  }
}
```

---

## 7. API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/companion/settings` | GET | Get user's companion settings |
| `/api/companion/settings` | PUT | Update companion settings |
| `/api/companion/prompt` | POST | Get personalized reflection prompt |
| `/api/companion/question` | POST | Get contemplative question |
| `/api/companion/meditation` | POST | Get meditation guidance script |
| `/api/companion/tts` | POST | Convert text to speech (returns audio) |

---

## 8. Key Files Quick Reference

### Backend Core Files

| File | Purpose |
|------|---------|
| `app/ai_providers/base.py` | Abstract AI provider interface |
| `app/ai_providers/openai_provider.py` | OpenAI implementation |
| `app/ai_providers/factory.py` | Provider factory |
| `app/companion/service.py` | Business logic |
| `app/companion/router.py` | API endpoints |
| `app/companion/prompts/system.py` | AI personality prompt |

### Frontend Core Files

| File | Purpose |
|------|---------|
| `src/contexts/CompanionContext.js` | State management |
| `src/hooks/useCompanion.js` | API interactions |
| `src/hooks/useMeditation.js` | Timer & session logic |
| `src/screens/companion/CompanionScreen.js` | Main screen |
| `src/screens/companion/MeditationScreen.js` | Meditation screen |
| `src/services/audioService.js` | Audio playback |

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OpenAI API unavailable | Fallback prompts/questions built-in |
| TTS fails | Show text guidance, continue session |
| Rate limits exceeded | Clear error message, retry guidance |
| Audio playback issues | Graceful degradation, text-only mode |
| Background audio fails | Test thoroughly on both platforms |

---

## 10. Future Enhancements (Out of Scope for v1)

- Conversation history persistence (optional)
- More meditation types
- Custom ambient sounds
- Offline AI (local models)
- Session statistics
- Streak tracking
- Export meditation history

---

## 11. Success Criteria Checklist

| Criteria | Status |
|----------|--------|
| User can open the Companion tab | ☐ |
| User can get personalized reflection prompts | ☐ |
| User can request contemplative questions | ☐ |
| User can start a guided meditation session | ☐ |
| Meditation includes timer with visual progress | ☐ |
| Meditation includes TTS voice guidance | ☐ |
| Tibetan bowl bell plays at start/end | ☐ |
| Audio plays in background when app minimized | ☐ |
| AI responses feel thoughtful and spiritual | ☐ |
| User can opt-in/out of reflection analysis | ☐ |
| No notifications or pushy behavior | ☐ |
| Provider can be switched via config | ☐ |
| Feature is tested | ☐ |
| Feature is documented | ☐ |

---

## 12. Implementation Order Recommendation

**Week 1: Backend Foundation**
1. AI provider abstraction layer
2. OpenAI provider implementation
3. Companion schemas and repository
4. Prompt templates

**Week 2: Backend API**
1. Companion service
2. Companion router
3. Rate limiting
4. Testing

**Week 3: Frontend Foundation**
1. Constants and API service
2. Audio service
3. Context and hooks
4. Basic components

**Week 4: Frontend Screens**
1. CompanionScreen
2. MeditationScreen
3. CompanionSettingsScreen
4. Navigation integration

**Week 5: Polish & Testing**
1. Audio refinement
2. UI polish
3. Testing
4. Bug fixes

---

## 13. Notes for Implementation

1. **Start with mock provider** - Test everything with mock before using real API
2. **Test audio early** - Background audio can be tricky on both platforms
3. **Keep prompts in separate files** - Easy to iterate on prompt engineering
4. **Rate limit from day 1** - Prevent runaway API costs
5. **Fallbacks everywhere** - Always have a graceful degradation path
6. **Test on real devices** - Audio behavior differs from simulator

---

## 14. Sign-off

This document completes the design phase for the AI Reflection Companion feature. All architectural decisions, API designs, component specifications, and implementation plans are documented in the `docs/ai-companion/` directory.

**Ready for implementation** upon your approval.

---

*Design completed: 2026-01-28*
