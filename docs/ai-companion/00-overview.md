# AI Reflection Companion - Feature Overview

## Document Info
- **Feature**: AI Reflection Companion
- **App**: Smriti
- **Created**: 2026-01-28
- **Status**: Design Phase

---

## 1. Feature Summary

The AI Reflection Companion is a thoughtful, spiritual AI assistant integrated into Smriti. It acts as a wise friend rather than a chatbot, helping users deepen their reflection and contemplation practice.

### Core Capabilities
1. **Personalized Reflection Prompts** - Based on user's past reflections
2. **Contemplative Questions** - To deepen practice
3. **Guided Meditation** - With audio, timer, and voice guidance

### Design Philosophy
- **User-initiated only** - No notifications, no reminders, no pushy behavior
- **Non-addictive** - Aligns with Smriti's minimal, intentional design
- **Privacy-first** - Explicit opt-in for reflection analysis
- **Thoughtful & Spiritual** - Calm UI, not like a chat app

---

## 2. Requirements

### 2.1 Backend Requirements

| Requirement | Description |
|-------------|-------------|
| AI Provider Integration | Support for OpenAI (primary), Anthropic, local models |
| Provider Abstraction | Easy switching between providers without code changes |
| Reflection Analysis | Analyze user's past posts to personalize prompts |
| Prompt Templates | Spiritual, thoughtful templates for each interaction type |
| TTS Support | Text-to-speech for meditation voice guidance |
| User Settings | Store opt-in preferences, companion settings |

### 2.2 Frontend Requirements

| Requirement | Description |
|-------------|-------------|
| New Tab | Dedicated "Companion" tab in bottom navigation (5 tabs total) |
| Calm UI | Peaceful interface, not chat-like |
| Reflection Prompts | Request and display personalized prompts |
| Contemplative Questions | Request and display deep questions |
| Meditation Screen | Timer, audio controls, guidance display |
| Audio System | Ambient sounds + TTS voice playback |
| Background Audio | Continue playing when app minimized |
| Settings | Opt-in toggle, preferences configuration |

### 2.3 Audio Requirements

| Feature | Description |
|---------|-------------|
| Ambient Sounds | Rain, forest, ocean, silence, tibetan bowl |
| Bell Sounds | Start bell, interval bells, end bell |
| TTS Integration | AI-generated voice for meditation guidance |
| Volume Control | Independent control for ambient and voice |
| Background Play | Audio continues when app is backgrounded |
| Audio Ducking | Lower ambient volume when TTS plays |

### 2.4 Meditation Timer Requirements

| Feature | Description |
|---------|-------------|
| Duration Presets | 5, 10, 15, 20, 30 minutes + custom |
| Interval Bells | Optional bells at set intervals |
| Session States | Idle, Preparing, Running, Paused, Completed, Cancelled |
| Visual Progress | Circular progress indicator |
| Guidance Types | Breath focus, body scan, loving-kindness, unguided |

---

## 3. Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Data Processing | Server-side | More powerful analysis, manageable app size |
| Reflection Opt-in | Explicit | Privacy-first, user control |
| Primary AI Provider | OpenAI | User preference, good TTS support |
| Provider Flexibility | Abstract factory pattern | Easy to switch providers |
| Conversation History | Ephemeral | Aligns with "letting go" philosophy |
| UI Placement | New bottom nav tab | Most accessible, prominent |
| Audio Approach | Ambient + TTS (Option C) | Full-featured meditation experience |
| Tab Count | 5 tabs (smaller icons) | Keep all features accessible |

---

## 4. Success Criteria

The feature is complete when:

- [ ] User can open the Companion tab
- [ ] User can get personalized reflection prompts based on past reflections
- [ ] User can request contemplative questions
- [ ] User can start a guided meditation session
- [ ] Meditation includes timer with visual progress
- [ ] Meditation includes ambient sound options
- [ ] Meditation includes TTS voice guidance
- [ ] Audio plays in background when app minimized
- [ ] AI responses feel thoughtful and spiritual
- [ ] User can opt-in/out of reflection analysis
- [ ] No notifications or pushy behavior
- [ ] Provider can be switched easily via configuration
- [ ] Feature is tested and documented

---

## 5. Out of Scope (v1)

- Conversation history persistence (intentionally ephemeral)
- Engagement notifications
- Algorithmic recommendations
- Social features (sharing AI responses)
- Offline AI (requires internet connection)

---

## 6. Document Index

| Document | Description |
|----------|-------------|
| [00-overview.md](./00-overview.md) | This document - feature overview |
| [01-architecture.md](./01-architecture.md) | System architecture design |
| [02-backend-api.md](./02-backend-api.md) | Backend schema & API design |
| [03-ai-providers.md](./03-ai-providers.md) | AI provider abstraction design |
| [04-frontend-components.md](./04-frontend-components.md) | Frontend component design |
| [05-prompt-engineering.md](./05-prompt-engineering.md) | Prompt templates design |
| [06-implementation-backend.md](./06-implementation-backend.md) | Backend implementation plan |
| [07-implementation-frontend.md](./07-implementation-frontend.md) | Frontend implementation plan |
| [08-testing.md](./08-testing.md) | Testing & documentation plan |
| [09-final-review.md](./09-final-review.md) | Final review & refinements |
