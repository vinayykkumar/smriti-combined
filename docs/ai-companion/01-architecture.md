# AI Reflection Companion - System Architecture

## Document Info
- **Feature**: AI Reflection Companion
- **Phase**: Architecture Design
- **Created**: 2026-01-28
- **Status**: Complete

---

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SMRITI APP                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         FRONTEND (React Native)                      │    │
│  │                                                                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │    │
│  │  │ Companion    │  │ Meditation   │  │ Audio System             │   │    │
│  │  │ Screen       │  │ Screen       │  │ ├─ Ambient Player        │   │    │
│  │  │ ├─ Prompts   │  │ ├─ Timer     │  │ ├─ TTS Player            │   │    │
│  │  │ ├─ Questions │  │ ├─ Intervals │  │ └─ Background Audio      │   │    │
│  │  │ └─ Chat UI   │  │ └─ Guidance  │  │                          │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘   │    │
│  │                                                                      │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │ CompanionContext + useCompanion() + useMeditation()          │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                      │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │ services/companionApi.js  │  services/audioService.js        │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                       │                                      │
│                                       ▼                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                              BACKEND (FastAPI)                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      companion/ module                               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │    │
│  │  │ router.py   │  │ service.py  │  │ schemas.py  │  │ prompts/  │  │    │
│  │  │ - /prompt   │  │ - generate  │  │ - Request   │  │ templates │  │    │
│  │  │ - /question │  │ - analyze   │  │ - Response  │  │           │  │    │
│  │  │ - /meditate │  │ - context   │  │ - Settings  │  │           │  │    │
│  │  │ - /tts      │  │             │  │             │  │           │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                       │                                      │
│                                       ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                 AI Provider Abstraction Layer                        │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │  AIProvider (Abstract Base Class)                           │    │    │
│  │  │  ├─ generate_completion(prompt, context) -> str             │    │    │
│  │  │  ├─ generate_tts(text) -> bytes                             │    │    │
│  │  │  └─ get_model_info() -> dict                                │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │           ▲                    ▲                    ▲                │    │
│  │           │                    │                    │                │    │
│  │  ┌────────┴───────┐  ┌────────┴───────┐  ┌────────┴───────┐        │    │
│  │  │ OpenAIProvider │  │AnthropicProvider│  │ LocalProvider  │        │    │
│  │  │ - GPT-4/3.5    │  │ - Claude        │  │ - Ollama       │        │    │
│  │  │ - TTS API      │  │ - (future TTS)  │  │ - Local TTS    │        │    │
│  │  └────────────────┘  └────────────────┘  └────────────────┘        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                       │                                      │
│                                       ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         MongoDB Atlas                                │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │    │
│  │  │ users           │  │ posts           │  │ companion_      │      │    │
│  │  │ + ai_opt_in     │  │ (reflections)   │  │ settings        │      │    │
│  │  │ + ai_settings   │  │                 │  │                 │      │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Module Structure

```
smriti-backend/app/
├── companion/
│   ├── __init__.py
│   ├── router.py              # API endpoints
│   ├── service.py             # Business logic
│   ├── schemas.py             # Pydantic models
│   ├── repository.py          # DB queries (settings)
│   ├── dependencies.py        # DI for AI provider
│   ├── constants.py           # Companion constants
│   └── prompts/
│       ├── __init__.py
│       ├── reflection.py      # Reflection prompt templates
│       ├── contemplation.py   # Contemplative question templates
│       ├── meditation.py      # Meditation guidance templates
│       └── system.py          # System prompts (personality)
│
├── ai_providers/
│   ├── __init__.py
│   ├── base.py                # Abstract base class
│   ├── openai_provider.py     # OpenAI implementation
│   ├── anthropic_provider.py  # Anthropic implementation
│   ├── local_provider.py      # Ollama/local models
│   ├── factory.py             # Provider factory
│   └── config.py              # Provider configuration
│
└── config/
    └── settings.py            # Add AI provider settings
```

---

## 3. Frontend Module Structure

```
smriti-frontend/src/
├── screens/
│   ├── companion/
│   │   ├── CompanionScreen.js        # Main companion tab
│   │   ├── MeditationScreen.js       # Meditation with timer/audio
│   │   ├── CompanionSettingsScreen.js # Opt-in, preferences
│   │   └── styles.js                  # Companion-specific styles
│
├── components/
│   ├── companion/
│   │   ├── CompanionCard.js          # Action cards (prompt/question/meditate)
│   │   ├── ResponseBubble.js         # AI response display (calm, not chatty)
│   │   ├── ReflectionPrompt.js       # Personalized prompt display
│   │   ├── ContemplativeQuestion.js  # Question display
│   │   └── InputArea.js              # User input (minimal)
│   │
│   ├── meditation/
│   │   ├── MeditationTimer.js        # Countdown timer
│   │   ├── TimerControls.js          # Start/pause/stop
│   │   ├── GuidanceTypePicker.js     # Sankalpam/Breath/Depth selection
│   │   ├── GuidanceDisplay.js        # TTS guidance text
│   │   └── ProgressRing.js           # Visual timer progress
│
├── contexts/
│   └── CompanionContext.js           # Companion state management
│
├── hooks/
│   ├── useCompanion.js               # Companion API interactions
│   ├── useMeditation.js              # Meditation timer logic
│   ├── useAudio.js                   # Audio playback management
│   └── useTTS.js                     # Text-to-speech handling
│
├── services/
│   ├── api/
│   │   └── companion.js              # Companion API calls
│   ├── audioService.js               # Audio playback service
│   └── ttsService.js                 # TTS audio handling
│
├── assets/
│   └── audio/
│       └── bells/
│           └── tibetan-bowl.mp3    # Used for start/end bells
│
└── constants/
    ├── companion.js                  # Companion constants
    └── meditation.js                 # Timer presets, audio config
```

---

## 4. Data Flow Diagrams

### 4.1 Personalized Reflection Prompt Flow

```
User taps "Get Reflection Prompt"
            │
            ▼
┌─────────────────────────────┐
│  Frontend: useCompanion()   │
│  calls companionApi.getPrompt()
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│  Backend: POST /companion/prompt
│  1. Check user opt-in status │
│  2. If opted-in:             │
│     - Fetch user's recent    │
│       reflections (posts)    │
│     - Extract themes/patterns│
│  3. Build context object     │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│  AI Provider Abstraction    │
│  1. Select prompt template   │
│  2. Inject user context      │
│  3. Call AI provider         │
│  4. Return generated prompt  │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│  Frontend: Display prompt   │
│  - Calm, thoughtful UI      │
│  - Optional: TTS playback   │
└─────────────────────────────┘
```

### 4.2 Meditation Session Flow

```
User configures meditation session
            │
            ▼
┌─────────────────────────────────────────┐
│  MeditationScreen                        │
│  1. Select duration (5-30 min)          │
│  2. Select ambient sound                │
│  3. Select guidance type                │
│  4. Configure interval bells            │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  If guidance enabled:                    │
│  POST /companion/meditation              │
│  - Get guidance script from AI          │
│  - Includes opening, intervals, closing │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  If TTS enabled:                         │
│  POST /companion/tts                     │
│  - Convert guidance text to audio       │
│  - Cache audio for session              │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  Session starts:                         │
│  1. Play start bell                     │
│  2. Start ambient sound (loop)          │
│  3. Play opening guidance (TTS)         │
│  4. Timer counts down                   │
│  5. Play interval bells/guidance        │
│  6. Play closing guidance               │
│  7. Play end bell                       │
│  8. Stop ambient sound (fade out)       │
└─────────────────────────────────────────┘
```

### 4.3 TTS Generation Flow

```
Text to convert to speech
            │
            ▼
┌─────────────────────────────┐
│  Backend: POST /companion/tts
│  1. Validate text length     │
│  2. Check rate limits        │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│  AI Provider (OpenAI TTS)   │
│  1. Select voice (calm tone)│
│  2. Generate audio stream   │
│  3. Return MP3/WAV bytes    │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│  Frontend receives audio    │
│  1. Cache in memory         │
│  2. Load into TTS player    │
│  3. Play when needed        │
└─────────────────────────────┘
```

---

## 5. Audio System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Audio Service (Frontend)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐             │
│  │  Ambient Player     │    │  TTS Player         │             │
│  │  ─────────────────  │    │  ─────────────────  │             │
│  │  - Loop playback    │    │  - One-shot play    │             │
│  │  - Volume control   │    │  - Queue guidance   │             │
│  │  - Fade in/out      │    │  - Stream from API  │             │
│  │  - Background audio │    │  - Cache responses  │             │
│  └─────────────────────┘    └─────────────────────┘             │
│            │                          │                          │
│            └──────────┬───────────────┘                          │
│                       ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Audio Focus Manager                         │    │
│  │  - Handle interruptions (calls, other apps)              │    │
│  │  - Background audio session (iOS/Android)                │    │
│  │  - Duck ambient when TTS plays                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Dependencies:                                                   │
│  - expo-av (audio playback)                                     │
│  - expo-keep-awake (prevent sleep during meditation)            │
└─────────────────────────────────────────────────────────────────┘
```

### Audio Ducking Behavior

When TTS guidance plays:
1. Detect TTS playback start
2. Reduce ambient volume to 30% (fade over 500ms)
3. Play TTS at full volume
4. Detect TTS playback end
5. Restore ambient volume to user setting (fade over 500ms)

### Background Audio Configuration

**iOS (app.json)**:
```json
{
  "ios": {
    "infoPlist": {
      "UIBackgroundModes": ["audio"]
    }
  }
}
```

**Android (app.json)**:
```json
{
  "android": {
    "permissions": ["android.permission.FOREGROUND_SERVICE"]
  }
}
```

---

## 6. Meditation Timer Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    Meditation Session                          │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Session Config:                                               │
│  ├─ duration: 5 | 10 | 15 | 20 | 30 | custom (minutes)       │
│  ├─ ambientSound: silence | tibetan-bowl                      │
│  ├─ startEndBell: tibetan-bowl (for session start/end)       │
│  ├─ guidanceType: none | sankalpam | breath-focus | depth-focus│
│  └─ guidanceTTS: boolean (play AI voice or text only)         │
│                                                                │
│  Session States:                                               │
│  ├─ IDLE → PREPARING → RUNNING → PAUSED → COMPLETED          │
│  └─ Can also → CANCELLED at any point                         │
│                                                                │
│  Guidance Flow (if enabled):                                   │
│  ├─ 0:00 - Opening guidance (TTS)                             │
│  ├─ 0:30 - Settling instruction                               │
│  ├─ intervals - Gentle reminders                              │
│  ├─ -1:00 - Closing begins                                    │
│  └─ 0:00 - Session complete                                   │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

### Timer State Machine

```
     ┌─────────┐
     │  IDLE   │ ◄──────────────────────────┐
     └────┬────┘                            │
          │ user taps "Start"               │
          ▼                                 │
    ┌───────────┐                           │
    │ PREPARING │ (loading audio, TTS)      │
    └─────┬─────┘                           │
          │ resources ready                 │
          ▼                                 │
    ┌───────────┐     user taps "Pause"     │
    │  RUNNING  │ ──────────────────────┐   │
    └─────┬─────┘                       │   │
          │                             ▼   │
          │                      ┌──────────┐
          │                      │  PAUSED  │
          │                      └────┬─────┘
          │                           │ user taps "Resume"
          │ ◄─────────────────────────┘
          │
          │ timer reaches 0
          ▼
    ┌───────────┐
    │ COMPLETED │ ──────────────────────────┘
    └───────────┘       user dismisses

    At any state (except IDLE/COMPLETED):
    user taps "Stop" → CANCELLED → IDLE
```

---

## 7. Navigation Structure Update

### Current Navigation (4 tabs)
```
Root (Bottom Tab Navigator)
├── Home Tab
├── Search Tab
├── Circles Tab
└── Profile Tab
```

### Updated Navigation (5 tabs)
```
Root (Bottom Tab Navigator)
├── Home Tab
│   ├── HomeScreen
│   ├── UserProfileScreen
│   └── PastQuotesScreen
├── Search Tab
│   ├── SearchScreen
│   └── UserProfileScreen
├── Companion Tab          ◄── NEW
│   ├── CompanionScreen
│   ├── MeditationScreen
│   └── CompanionSettingsScreen
├── Circles Tab
│   ├── CirclesListScreen
│   ├── CircleFeedScreen
│   ├── CircleSettingsScreen
│   └── UserProfileScreen
└── Profile Tab
    ├── ProfileScreen
    └── UserProfileScreen
```

### Tab Bar Design

With 5 tabs, each tab icon will be slightly smaller:
- Icon size: 22px (down from 24px)
- Label font size: 10px (down from 11px)
- Tab width: 20% of screen width each

---

## 8. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| AI Provider Pattern | Abstract Factory | Easy to swap OpenAI ↔ Anthropic ↔ Local without code changes |
| TTS Provider | OpenAI TTS API (primary) | Same provider as chat, high quality, simple billing |
| TTS Voice | `nova` or `shimmer` | Calm, warm voices suitable for meditation |
| Conversation Storage | Ephemeral (not stored) | Aligns with "letting go" philosophy, simpler, more private |
| Reflection Analysis | On-demand, not cached | Fresh context each time, respects latest reflections |
| Audio Library | expo-av | Already in Expo ecosystem, supports background audio |
| Timer State | useMeditation hook | Encapsulates all timer logic, easy to test |
| Background Audio | Native audio session | Required for meditation to continue when phone locked |

---

## 9. Security Considerations

### API Key Management
- AI provider keys stored in backend `.env` only
- Never exposed to frontend
- Rate limiting on all companion endpoints

### User Data Privacy
- Reflection analysis requires explicit opt-in
- Analysis happens server-side, no data sent to third parties beyond AI provider
- AI provider API calls don't store conversation history (ephemeral)
- No personal data included in AI prompts beyond reflection content

### Audio File Security
- Ambient sounds bundled with app (no external URLs)
- TTS audio generated per-request, not cached on server
- TTS audio cached temporarily on device during session only

---

## 10. Dependencies to Add

### Backend (requirements.txt)
```
openai>=1.0.0           # OpenAI API (chat + TTS)
anthropic>=0.18.0       # Anthropic API (optional)
httpx>=0.25.0           # Async HTTP client for local models
```

### Frontend (package.json)
```json
{
  "expo-av": "~14.0.0",           // Audio playback
  "expo-keep-awake": "~13.0.0"    // Prevent sleep during meditation
}
```

Note: expo-av and expo-keep-awake may already be available in Expo SDK 54.

---

## 11. Resolved Decisions

| Question | Decision |
|----------|----------|
| TTS Voice | **nova** - warm, calm voice |
| Ambient Sounds | **Silence + Tibetan Bowl** (bowl for start/end bells only) |
| Meditation Types | **Sankalpam, Breath Focus, Depth Focus** |
