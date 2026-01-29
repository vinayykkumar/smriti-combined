# AI Reflection Companion - Frontend Component Design

## Document Info
- **Feature**: AI Reflection Companion
- **Phase**: Frontend Component Design
- **Created**: 2026-01-28
- **Status**: Complete

---

## 1. Component Hierarchy

```
CompanionTab (Bottom Navigation)
│
├── CompanionStackNavigator
│   │
│   ├── CompanionScreen (Main)
│   │   ├── CompanionHeader
│   │   ├── ActionCardsSection
│   │   │   ├── ReflectionPromptCard
│   │   │   ├── ContemplativeQuestionCard
│   │   │   └── MeditationCard
│   │   ├── ResponseSection (conditional)
│   │   │   ├── ResponseBubble
│   │   │   └── TTSControls
│   │   └── OptInBanner (if not opted in)
│   │
│   ├── MeditationScreen
│   │   ├── MeditationHeader
│   │   ├── DurationPicker
│   │   ├── GuidanceTypePicker
│   │   ├── ProgressRing
│   │   ├── TimerDisplay
│   │   ├── GuidanceDisplay
│   │   └── TimerControls
│   │
│   └── CompanionSettingsScreen
│       ├── OptInSection
│       ├── PreferencesSection
│       └── AboutSection
```

---

## 2. Screen Designs

### 2.1 CompanionScreen (Main)

**Purpose**: Main hub for AI companion interactions

**Layout**:
```
┌─────────────────────────────────────┐
│  ⚙️                    Companion    │  <- Header with settings
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │  🪷 Reflection Prompt        │   │  <- Action Card 1
│  │  Get a personalized prompt   │   │
│  │  based on your journey       │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  💭 Contemplative Question   │   │  <- Action Card 2
│  │  Explore deeper aspects      │   │
│  │  of your practice            │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  🧘 Guided Meditation        │   │  <- Action Card 3
│  │  Sankalpam • Breath • Depth  │   │
│  └─────────────────────────────┘   │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  [Response area - shows when       │  <- Response Section
│   user requests something]          │
│                                     │
│                                     │
└─────────────────────────────────────┘
│ 🏠  🔍  🪷  ⭕  👤 │  <- Bottom nav (5 tabs)
└─────────────────────────────────────┘
```

**States**:
- Default: Shows action cards
- Loading: Shows gentle loading indicator
- Response: Shows AI response with TTS option
- Error: Shows error message with retry

---

### 2.2 MeditationScreen

**Purpose**: Guided meditation with timer and TTS

**Layout (Setup Phase)**:
```
┌─────────────────────────────────────┐
│  ←  Meditation                      │
├─────────────────────────────────────┤
│                                     │
│         How long?                   │
│                                     │
│    ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐   │
│    │ 5 │ │10 │ │15 │ │20 │ │30 │   │  <- Duration pills
│    └───┘ └───┘ └───┘ └───┘ └───┘   │
│                                     │
│         Guidance Type               │
│                                     │
│    ┌─────────────────────────┐     │
│    │  🙏 Sankalpam            │     │  <- Type selector
│    │  Set your intention      │     │
│    └─────────────────────────┘     │
│    ┌─────────────────────────┐     │
│    │  🌬️ Breath Focus         │     │
│    │  Awareness of breath     │     │
│    └─────────────────────────┘     │
│    ┌─────────────────────────┐     │
│    │  🌊 Depth Focus          │     │
│    │  Deep contemplation      │     │
│    └─────────────────────────┘     │
│                                     │
│    ┌─────────────────────────┐     │
│    │      Begin Session       │     │  <- Start button
│    └─────────────────────────┘     │
│                                     │
└─────────────────────────────────────┘
```

**Layout (Active Session)**:
```
┌─────────────────────────────────────┐
│                                     │
│                                     │
│           ╭───────────╮             │
│          ╱             ╲            │
│         │    12:34     │            │  <- Progress ring + timer
│          ╲             ╱            │
│           ╰───────────╯             │
│                                     │
│         Breath Focus                │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │  "Allow your breath to      │   │  <- Guidance text
│  │   find its natural rhythm.  │   │
│  │   There is no need to       │   │
│  │   change anything..."       │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│         🔊 ────●──── Volume         │  <- Volume slider
│                                     │
│      ⏸️ Pause      ⏹️ End           │  <- Controls
│                                     │
└─────────────────────────────────────┘
```

**States**:
- Setup: Configuration options
- Preparing: Loading guidance, TTS
- Running: Timer active, guidance displayed
- Paused: Timer paused, can resume
- Completed: Session summary

---

### 2.3 CompanionSettingsScreen

**Purpose**: Manage companion preferences and opt-in

**Layout**:
```
┌─────────────────────────────────────┐
│  ←  Companion Settings              │
├─────────────────────────────────────┤
│                                     │
│  REFLECTION ANALYSIS                │
│  ┌─────────────────────────────┐   │
│  │  Personalize prompts based  │   │
│  │  on your past reflections   │   │
│  │                      [ON]   │   │  <- Toggle
│  │                             │   │
│  │  Your reflections are only  │   │
│  │  analyzed when you request  │   │
│  │  a prompt. Never stored.    │   │
│  └─────────────────────────────┘   │
│                                     │
│  PREFERENCES                        │
│  ┌─────────────────────────────┐   │
│  │  Default Duration     10min │   │
│  │  Guidance Type    Breath ▼  │   │
│  │  Voice Guidance       [ON]  │   │
│  │  Show Text            [ON]  │   │
│  └─────────────────────────────┘   │
│                                     │
│  ABOUT                              │
│  ┌─────────────────────────────┐   │
│  │  The AI Companion is here   │   │
│  │  to support your practice,  │   │
│  │  not replace your wisdom.   │   │
│  │  Use it mindfully.          │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

---

## 3. Component Specifications

### 3.1 CompanionCard

**Purpose**: Action card for prompts, questions, meditation

**Props**:
```typescript
interface CompanionCardProps {
  icon: string;               // Emoji or icon name
  title: string;              // Card title
  description: string;        // Brief description
  onPress: () => void;        // Tap handler
  disabled?: boolean;         // Disable interactions
  loading?: boolean;          // Show loading state
  variant?: 'default' | 'active';  // Visual variant
}
```

**Styling**:
```javascript
// Using existing theme
const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.card,      // #F5EEE6
    borderRadius: theme.borderRadius.lg,     // 16
    padding: theme.spacing.lg,               // 24
    marginBottom: theme.spacing.md,          // 16
    ...theme.shadows.small
  },
  cardActive: {
    borderWidth: 2,
    borderColor: theme.colors.primary        // #4E342E
  },
  icon: {
    fontSize: 28,
    marginBottom: theme.spacing.sm           // 8
  },
  title: {
    fontFamily: theme.fonts.serif,
    fontSize: theme.fontSizes.heading,       // 20
    color: theme.colors.text,                // #2C1810
    marginBottom: theme.spacing.xs           // 4
  },
  description: {
    fontFamily: theme.fonts.serif,
    fontSize: theme.fontSizes.body,          // 16
    color: theme.colors.textSecondary,       // #5D4E47
    lineHeight: 22
  }
});
```

---

### 3.2 ResponseBubble

**Purpose**: Display AI response in calm, readable format

**Props**:
```typescript
interface ResponseBubbleProps {
  text: string;               // AI response text
  isLoading?: boolean;        // Show typing indicator
  onTTSPlay?: () => void;     // Play TTS button
  onTTSStop?: () => void;     // Stop TTS button
  ttsPlaying?: boolean;       // TTS playback state
  showTTS?: boolean;          // Show TTS controls
}
```

**Layout**:
```
┌─────────────────────────────────────┐
│                                     │
│  "Consider what brings you peace   │
│   in this present moment. Your     │
│   recent reflections speak of      │
│   seeking stillness amid change.   │
│                                     │
│   What would it mean to find       │
│   peace not despite the change,    │
│   but within it?"                  │
│                                     │
│              🔊 Listen              │  <- TTS button
└─────────────────────────────────────┘
```

**Styling**:
- Background: Slightly darker than page (#EDE4DA)
- Font: Serif, larger line-height for readability
- Padding: Generous (24px)
- Border radius: Large (20px) for soft feel

---

### 3.3 ProgressRing

**Purpose**: Circular progress indicator for meditation timer

**Props**:
```typescript
interface ProgressRingProps {
  progress: number;           // 0-1 progress value
  size: number;               // Ring diameter
  strokeWidth: number;        // Ring thickness
  duration: number;           // Total duration in seconds
  remaining: number;          // Remaining time in seconds
  isActive: boolean;          // Animation active
  isPaused: boolean;          // Paused state
}
```

**Implementation Notes**:
- Use `react-native-svg` for smooth circular progress
- Animate with `Animated` API
- Show time in MM:SS format in center
- Subtle glow effect when active

---

### 3.4 GuidanceTypePicker

**Purpose**: Select meditation guidance type

**Props**:
```typescript
interface GuidanceTypePickerProps {
  selected: 'sankalpam' | 'breath-focus' | 'depth-focus';
  onSelect: (type: string) => void;
  disabled?: boolean;
}

// Type definitions
const GUIDANCE_TYPES = {
  'sankalpam': {
    icon: '🙏',
    title: 'Sankalpam',
    description: 'Set your intention and resolve'
  },
  'breath-focus': {
    icon: '🌬️',
    title: 'Breath Focus',
    description: 'Awareness of natural breathing'
  },
  'depth-focus': {
    icon: '🌊',
    title: 'Depth Focus',
    description: 'Deep contemplative stillness'
  }
};
```

---

### 3.5 TimerControls

**Purpose**: Control meditation session

**Props**:
```typescript
interface TimerControlsProps {
  state: 'idle' | 'preparing' | 'running' | 'paused' | 'completed';
  onStart: () => void;
  onPause: () => void;
  onResume: () => void;
  onStop: () => void;
  onComplete: () => void;
}
```

**Button States**:
| State | Left Button | Right Button |
|-------|-------------|--------------|
| idle | "Begin Session" (full width) | - |
| preparing | "Preparing..." (disabled) | - |
| running | "Pause" | "End Session" |
| paused | "Resume" | "End Session" |
| completed | "New Session" | "Done" |

---

### 3.6 GuidanceDisplay

**Purpose**: Show current meditation guidance text

**Props**:
```typescript
interface GuidanceDisplayProps {
  text: string;               // Current guidance text
  isVisible: boolean;         // Show/hide
  animate?: boolean;          // Fade in animation
}
```

**Styling**:
- Centered text
- Serif font, italic
- Larger size (18px)
- High line-height (28px)
- Generous padding
- Subtle background

---

### 3.7 OptInBanner

**Purpose**: Encourage opt-in for personalized prompts

**Props**:
```typescript
interface OptInBannerProps {
  onOptIn: () => void;
  onDismiss: () => void;
  dismissed: boolean;
}
```

**Layout**:
```
┌─────────────────────────────────────┐
│  ✨ Personalize your experience     │
│                                     │
│  Allow reflection analysis for      │
│  prompts tailored to your journey   │
│                                     │
│  [Enable]            [Not now]      │
└─────────────────────────────────────┘
```

---

## 4. Context & Hooks

### 4.1 CompanionContext

**Purpose**: Manage companion state across screens

```javascript
// src/contexts/CompanionContext.js

import React, { createContext, useContext, useReducer, useCallback } from 'react';

const CompanionContext = createContext(null);

const initialState = {
  // Settings
  settings: {
    optInReflectionAnalysis: false,
    preferredGuidanceType: 'breath-focus',
    preferredTTSVoice: 'nova',
    defaultMeditationDuration: 10,
    showGuidanceText: true,
    settingsLoaded: false
  },

  // Current response
  response: {
    text: null,
    type: null,  // 'prompt' | 'question' | null
    themes: [],
    basedOnReflections: false
  },

  // Loading states
  isLoading: false,
  error: null,

  // TTS state
  tts: {
    isPlaying: false,
    isLoading: false,
    audioUri: null
  }
};

const companionReducer = (state, action) => {
  switch (action.type) {
    case 'SET_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload, settingsLoaded: true }
      };

    case 'SET_LOADING':
      return { ...state, isLoading: action.payload, error: null };

    case 'SET_RESPONSE':
      return {
        ...state,
        response: action.payload,
        isLoading: false,
        error: null
      };

    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };

    case 'CLEAR_RESPONSE':
      return {
        ...state,
        response: { text: null, type: null, themes: [], basedOnReflections: false }
      };

    case 'SET_TTS_STATE':
      return { ...state, tts: { ...state.tts, ...action.payload } };

    default:
      return state;
  }
};

export const CompanionProvider = ({ children }) => {
  const [state, dispatch] = useReducer(companionReducer, initialState);

  return (
    <CompanionContext.Provider value={{ state, dispatch }}>
      {children}
    </CompanionContext.Provider>
  );
};

export const useCompanionContext = () => {
  const context = useContext(CompanionContext);
  if (!context) {
    throw new Error('useCompanionContext must be used within CompanionProvider');
  }
  return context;
};
```

---

### 4.2 useCompanion Hook

**Purpose**: API interactions for companion features

```javascript
// src/hooks/useCompanion.js

import { useCallback } from 'react';
import { useCompanionContext } from '../contexts/CompanionContext';
import * as companionApi from '../services/api/companion';

export const useCompanion = () => {
  const { state, dispatch } = useCompanionContext();

  // Fetch settings on mount
  const loadSettings = useCallback(async () => {
    try {
      const settings = await companionApi.getSettings();
      dispatch({ type: 'SET_SETTINGS', payload: settings });
    } catch (error) {
      console.error('Failed to load companion settings:', error);
    }
  }, [dispatch]);

  // Update settings
  const updateSettings = useCallback(async (updates) => {
    try {
      const settings = await companionApi.updateSettings(updates);
      dispatch({ type: 'SET_SETTINGS', payload: settings });
      return settings;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  }, [dispatch]);

  // Get reflection prompt
  const getReflectionPrompt = useCallback(async (options = {}) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const result = await companionApi.getReflectionPrompt(options);
      dispatch({
        type: 'SET_RESPONSE',
        payload: {
          text: result.prompt,
          type: 'prompt',
          themes: result.reflection_themes || [],
          basedOnReflections: result.based_on_reflections
        }
      });
      return result;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  }, [dispatch]);

  // Get contemplative question
  const getContemplativeQuestion = useCallback(async (options = {}) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const result = await companionApi.getContemplativeQuestion(options);
      dispatch({
        type: 'SET_RESPONSE',
        payload: {
          text: result.question,
          type: 'question',
          themes: [],
          basedOnReflections: false,
          followUps: result.follow_up_prompts
        }
      });
      return result;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  }, [dispatch]);

  // Clear current response
  const clearResponse = useCallback(() => {
    dispatch({ type: 'CLEAR_RESPONSE' });
  }, [dispatch]);

  return {
    // State
    settings: state.settings,
    response: state.response,
    isLoading: state.isLoading,
    error: state.error,

    // Actions
    loadSettings,
    updateSettings,
    getReflectionPrompt,
    getContemplativeQuestion,
    clearResponse
  };
};
```

---

### 4.3 useMeditation Hook

**Purpose**: Meditation session management

```javascript
// src/hooks/useMeditation.js

import { useReducer, useCallback, useRef, useEffect } from 'react';
import * as companionApi from '../services/api/companion';
import { audioService } from '../services/audioService';

const initialState = {
  // Session config
  duration: 10,           // minutes
  guidanceType: 'breath-focus',

  // Session state
  status: 'idle',         // idle | preparing | running | paused | completed
  remainingSeconds: 0,

  // Guidance
  guidance: null,         // { opening, settling, intervals, closing }
  currentGuidanceText: '',

  // TTS
  ttsEnabled: true,
  ttsLoading: false,

  // Audio
  volume: 0.8
};

const meditationReducer = (state, action) => {
  switch (action.type) {
    case 'SET_CONFIG':
      return { ...state, ...action.payload };

    case 'SET_STATUS':
      return { ...state, status: action.payload };

    case 'SET_REMAINING':
      return { ...state, remainingSeconds: action.payload };

    case 'SET_GUIDANCE':
      return { ...state, guidance: action.payload };

    case 'SET_CURRENT_GUIDANCE_TEXT':
      return { ...state, currentGuidanceText: action.payload };

    case 'SET_TTS_LOADING':
      return { ...state, ttsLoading: action.payload };

    case 'SET_VOLUME':
      return { ...state, volume: action.payload };

    case 'RESET':
      return { ...initialState, duration: state.duration, guidanceType: state.guidanceType };

    default:
      return state;
  }
};

export const useMeditation = () => {
  const [state, dispatch] = useReducer(meditationReducer, initialState);
  const timerRef = useRef(null);
  const guidanceTimersRef = useRef([]);

  // Configure session
  const setDuration = useCallback((minutes) => {
    dispatch({ type: 'SET_CONFIG', payload: { duration: minutes, remainingSeconds: minutes * 60 } });
  }, []);

  const setGuidanceType = useCallback((type) => {
    dispatch({ type: 'SET_CONFIG', payload: { guidanceType: type } });
  }, []);

  // Start session
  const startSession = useCallback(async () => {
    dispatch({ type: 'SET_STATUS', payload: 'preparing' });
    dispatch({ type: 'SET_REMAINING', payload: state.duration * 60 });

    try {
      // Fetch guidance from AI
      const guidance = await companionApi.getMeditationGuidance({
        duration_minutes: state.duration,
        guidance_type: state.guidanceType,
        include_intervals: true,
        interval_minutes: Math.max(1, Math.floor(state.duration / 3))
      });

      dispatch({ type: 'SET_GUIDANCE', payload: guidance });

      // Play start bell
      await audioService.playBell('start');

      // Start timer
      dispatch({ type: 'SET_STATUS', payload: 'running' });

      // Show opening guidance
      dispatch({ type: 'SET_CURRENT_GUIDANCE_TEXT', payload: guidance.opening });

      // Play TTS for opening
      if (state.ttsEnabled) {
        await playGuidanceTTS(guidance.opening);
      }

      // Schedule interval guidance
      scheduleIntervalGuidance(guidance, state.duration * 60);

      // Start countdown
      startTimer();

    } catch (error) {
      console.error('Failed to start meditation:', error);
      dispatch({ type: 'SET_STATUS', payload: 'idle' });
    }
  }, [state.duration, state.guidanceType, state.ttsEnabled]);

  // Timer logic
  const startTimer = useCallback(() => {
    timerRef.current = setInterval(() => {
      dispatch((prevState) => {
        const newRemaining = prevState.remainingSeconds - 1;

        if (newRemaining <= 0) {
          clearInterval(timerRef.current);
          completeSession();
          return { type: 'SET_REMAINING', payload: 0 };
        }

        return { type: 'SET_REMAINING', payload: newRemaining };
      });
    }, 1000);
  }, []);

  // Pause session
  const pauseSession = useCallback(() => {
    clearInterval(timerRef.current);
    dispatch({ type: 'SET_STATUS', payload: 'paused' });
    audioService.pause();
  }, []);

  // Resume session
  const resumeSession = useCallback(() => {
    dispatch({ type: 'SET_STATUS', payload: 'running' });
    startTimer();
    audioService.resume();
  }, [startTimer]);

  // End session early
  const endSession = useCallback(async () => {
    clearInterval(timerRef.current);
    guidanceTimersRef.current.forEach(t => clearTimeout(t));
    audioService.stop();
    await audioService.playBell('end');
    dispatch({ type: 'SET_STATUS', payload: 'completed' });
  }, []);

  // Complete session
  const completeSession = useCallback(async () => {
    if (state.guidance?.closing) {
      dispatch({ type: 'SET_CURRENT_GUIDANCE_TEXT', payload: state.guidance.closing });
      if (state.ttsEnabled) {
        await playGuidanceTTS(state.guidance.closing);
      }
    }
    await audioService.playBell('end');
    dispatch({ type: 'SET_STATUS', payload: 'completed' });
  }, [state.guidance, state.ttsEnabled]);

  // Reset for new session
  const resetSession = useCallback(() => {
    clearInterval(timerRef.current);
    guidanceTimersRef.current.forEach(t => clearTimeout(t));
    audioService.stop();
    dispatch({ type: 'RESET' });
  }, []);

  // Play TTS
  const playGuidanceTTS = async (text) => {
    dispatch({ type: 'SET_TTS_LOADING', payload: true });
    try {
      const audioData = await companionApi.textToSpeech({ text });
      await audioService.playTTS(audioData);
    } catch (error) {
      console.error('TTS playback failed:', error);
    } finally {
      dispatch({ type: 'SET_TTS_LOADING', payload: false });
    }
  };

  // Schedule interval guidance
  const scheduleIntervalGuidance = (guidance, totalSeconds) => {
    if (!guidance.intervals?.length) return;

    const intervalCount = guidance.intervals.length;
    const intervalDuration = totalSeconds / (intervalCount + 1);

    guidance.intervals.forEach((text, index) => {
      const timer = setTimeout(async () => {
        dispatch({ type: 'SET_CURRENT_GUIDANCE_TEXT', payload: text });
        if (state.ttsEnabled) {
          await playGuidanceTTS(text);
        }
      }, intervalDuration * (index + 1) * 1000);

      guidanceTimersRef.current.push(timer);
    });

    // Schedule closing guidance
    const closingTimer = setTimeout(async () => {
      dispatch({ type: 'SET_CURRENT_GUIDANCE_TEXT', payload: guidance.closing });
      if (state.ttsEnabled) {
        await playGuidanceTTS(guidance.closing);
      }
    }, (totalSeconds - 60) * 1000); // 1 minute before end

    guidanceTimersRef.current.push(closingTimer);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearInterval(timerRef.current);
      guidanceTimersRef.current.forEach(t => clearTimeout(t));
    };
  }, []);

  return {
    // State
    duration: state.duration,
    guidanceType: state.guidanceType,
    status: state.status,
    remainingSeconds: state.remainingSeconds,
    currentGuidanceText: state.currentGuidanceText,
    ttsEnabled: state.ttsEnabled,
    ttsLoading: state.ttsLoading,
    volume: state.volume,

    // Computed
    progress: state.duration > 0
      ? 1 - (state.remainingSeconds / (state.duration * 60))
      : 0,

    // Actions
    setDuration,
    setGuidanceType,
    startSession,
    pauseSession,
    resumeSession,
    endSession,
    resetSession,
    setVolume: (v) => dispatch({ type: 'SET_VOLUME', payload: v }),
    setTTSEnabled: (v) => dispatch({ type: 'SET_CONFIG', payload: { ttsEnabled: v } })
  };
};
```

---

### 4.4 useAudio Hook

**Purpose**: Audio playback management

```javascript
// src/hooks/useAudio.js

import { useState, useCallback, useRef, useEffect } from 'react';
import { Audio } from 'expo-av';

export const useAudio = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const soundRef = useRef(null);

  // Initialize audio mode
  useEffect(() => {
    const setupAudio = async () => {
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        staysActiveInBackground: true,  // Continue in background
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false
      });
    };
    setupAudio();

    return () => {
      if (soundRef.current) {
        soundRef.current.unloadAsync();
      }
    };
  }, []);

  // Load and play audio from URI
  const playFromUri = useCallback(async (uri, options = {}) => {
    setIsLoading(true);
    try {
      // Unload previous sound
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
      }

      const { sound } = await Audio.Sound.createAsync(
        { uri },
        {
          shouldPlay: true,
          volume: options.volume ?? 1.0,
          isLooping: options.loop ?? false
        }
      );

      soundRef.current = sound;
      setIsPlaying(true);

      // Listen for completion
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.didJustFinish) {
          setIsPlaying(false);
          options.onComplete?.();
        }
      });

    } catch (error) {
      console.error('Audio playback error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load and play from local asset
  const playFromAsset = useCallback(async (asset, options = {}) => {
    setIsLoading(true);
    try {
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
      }

      const { sound } = await Audio.Sound.createAsync(
        asset,
        {
          shouldPlay: true,
          volume: options.volume ?? 1.0,
          isLooping: options.loop ?? false
        }
      );

      soundRef.current = sound;
      setIsPlaying(true);

      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.didJustFinish) {
          setIsPlaying(false);
          options.onComplete?.();
        }
      });

    } catch (error) {
      console.error('Audio playback error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Pause playback
  const pause = useCallback(async () => {
    if (soundRef.current) {
      await soundRef.current.pauseAsync();
      setIsPlaying(false);
    }
  }, []);

  // Resume playback
  const resume = useCallback(async () => {
    if (soundRef.current) {
      await soundRef.current.playAsync();
      setIsPlaying(true);
    }
  }, []);

  // Stop and unload
  const stop = useCallback(async () => {
    if (soundRef.current) {
      await soundRef.current.stopAsync();
      await soundRef.current.unloadAsync();
      soundRef.current = null;
      setIsPlaying(false);
    }
  }, []);

  // Set volume
  const setVolume = useCallback(async (volume) => {
    if (soundRef.current) {
      await soundRef.current.setVolumeAsync(volume);
    }
  }, []);

  return {
    isPlaying,
    isLoading,
    playFromUri,
    playFromAsset,
    pause,
    resume,
    stop,
    setVolume
  };
};
```

---

## 5. Services

### 5.1 Companion API Service

```javascript
// src/services/api/companion.js

import apiClient from './client';

/**
 * Get companion settings
 */
export const getSettings = async () => {
  const response = await apiClient.get('/companion/settings');
  return response.data.data;
};

/**
 * Update companion settings
 */
export const updateSettings = async (updates) => {
  const response = await apiClient.put('/companion/settings', updates);
  return response.data.data;
};

/**
 * Get personalized reflection prompt
 */
export const getReflectionPrompt = async (options = {}) => {
  const response = await apiClient.post('/companion/prompt', {
    context: options.context || null,
    mood: options.mood || null
  });
  return response.data.data;
};

/**
 * Get contemplative question
 */
export const getContemplativeQuestion = async (options = {}) => {
  const response = await apiClient.post('/companion/question', {
    category: options.category || null,
    depth: options.depth || 'moderate'
  });
  return response.data.data;
};

/**
 * Get meditation guidance
 */
export const getMeditationGuidance = async (options) => {
  const response = await apiClient.post('/companion/meditation', {
    duration_minutes: options.duration_minutes,
    guidance_type: options.guidance_type,
    include_intervals: options.include_intervals ?? true,
    interval_minutes: options.interval_minutes ?? 5
  });
  return response.data.data;
};

/**
 * Text to speech
 * Returns audio blob/base64
 */
export const textToSpeech = async (options) => {
  const response = await apiClient.post('/companion/tts', {
    text: options.text,
    voice: options.voice || null
  }, {
    responseType: 'blob'
  });
  return response.data;
};
```

---

### 5.2 Audio Service

```javascript
// src/services/audioService.js

import { Audio } from 'expo-av';

// Bell sound asset
const BELL_SOUND = require('../assets/audio/bells/tibetan-bowl.mp3');

class AudioService {
  constructor() {
    this.bellSound = null;
    this.ttsSound = null;
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;

    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
      staysActiveInBackground: true,
      playsInSilentModeIOS: true,
      shouldDuckAndroid: true,
      playThroughEarpieceAndroid: false
    });

    this.initialized = true;
  }

  async playBell(type = 'start') {
    await this.initialize();

    try {
      // Unload previous bell if any
      if (this.bellSound) {
        await this.bellSound.unloadAsync();
      }

      const { sound } = await Audio.Sound.createAsync(
        BELL_SOUND,
        { shouldPlay: true, volume: 0.8 }
      );

      this.bellSound = sound;

      // Auto-unload when done
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.didJustFinish) {
          sound.unloadAsync();
          this.bellSound = null;
        }
      });

    } catch (error) {
      console.error('Bell playback error:', error);
    }
  }

  async playTTS(audioBlob) {
    await this.initialize();

    try {
      // Unload previous TTS if any
      if (this.ttsSound) {
        await this.ttsSound.unloadAsync();
      }

      // Convert blob to base64 URI or use blob URL
      const uri = URL.createObjectURL(audioBlob);

      const { sound } = await Audio.Sound.createAsync(
        { uri },
        { shouldPlay: true, volume: 1.0 }
      );

      this.ttsSound = sound;

      return new Promise((resolve) => {
        sound.setOnPlaybackStatusUpdate((status) => {
          if (status.didJustFinish) {
            sound.unloadAsync();
            this.ttsSound = null;
            resolve();
          }
        });
      });

    } catch (error) {
      console.error('TTS playback error:', error);
      throw error;
    }
  }

  async pause() {
    if (this.ttsSound) {
      await this.ttsSound.pauseAsync();
    }
  }

  async resume() {
    if (this.ttsSound) {
      await this.ttsSound.playAsync();
    }
  }

  async stop() {
    if (this.bellSound) {
      await this.bellSound.stopAsync();
      await this.bellSound.unloadAsync();
      this.bellSound = null;
    }
    if (this.ttsSound) {
      await this.ttsSound.stopAsync();
      await this.ttsSound.unloadAsync();
      this.ttsSound = null;
    }
  }
}

export const audioService = new AudioService();
```

---

## 6. Navigation Updates

### 6.1 Add Companion Tab

```javascript
// src/navigation/AppNavigator.js (updates)

import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import CompanionStackNavigator from './CompanionStackNavigator';

const Tab = createBottomTabNavigator();

// Update tab navigator to include Companion
<Tab.Navigator
  screenOptions={{
    tabBarStyle: {
      backgroundColor: theme.colors.background,
      borderTopColor: theme.colors.border,
      height: 60,
      paddingBottom: 8
    },
    tabBarActiveTintColor: theme.colors.primary,
    tabBarInactiveTintColor: theme.colors.textSecondary,
    tabBarLabelStyle: {
      fontSize: 10,  // Smaller for 5 tabs
      fontFamily: theme.fonts.sans
    },
    tabBarIconStyle: {
      marginTop: 4
    }
  }}
>
  <Tab.Screen
    name="Home"
    component={HomeStackNavigator}
    options={{
      tabBarIcon: ({ color }) => <HomeIcon color={color} size={22} />,
      headerShown: false
    }}
  />
  <Tab.Screen
    name="Search"
    component={SearchStackNavigator}
    options={{
      tabBarIcon: ({ color }) => <SearchIcon color={color} size={22} />,
      headerShown: false
    }}
  />
  <Tab.Screen
    name="Companion"
    component={CompanionStackNavigator}
    options={{
      tabBarIcon: ({ color }) => <CompanionIcon color={color} size={22} />,
      headerShown: false
    }}
  />
  <Tab.Screen
    name="Circles"
    component={CirclesStackNavigator}
    options={{
      tabBarIcon: ({ color }) => <CirclesIcon color={color} size={22} />,
      headerShown: false
    }}
  />
  <Tab.Screen
    name="Profile"
    component={ProfileStackNavigator}
    options={{
      tabBarIcon: ({ color }) => <ProfileIcon color={color} size={22} />,
      headerShown: false
    }}
  />
</Tab.Navigator>
```

### 6.2 Companion Stack Navigator

```javascript
// src/navigation/CompanionStackNavigator.js

import { createNativeStackNavigator } from '@react-navigation/native-stack';
import CompanionScreen from '../screens/companion/CompanionScreen';
import MeditationScreen from '../screens/companion/MeditationScreen';
import CompanionSettingsScreen from '../screens/companion/CompanionSettingsScreen';

const Stack = createNativeStackNavigator();

const CompanionStackNavigator = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: theme.colors.background }
      }}
    >
      <Stack.Screen name="CompanionMain" component={CompanionScreen} />
      <Stack.Screen name="Meditation" component={MeditationScreen} />
      <Stack.Screen name="CompanionSettings" component={CompanionSettingsScreen} />
    </Stack.Navigator>
  );
};

export default CompanionStackNavigator;
```

---

## 7. Constants

```javascript
// src/constants/companion.js

export const GUIDANCE_TYPES = {
  'sankalpam': {
    id: 'sankalpam',
    icon: '🙏',
    title: 'Sankalpam',
    description: 'Set your intention and resolve',
    shortDescription: 'Intention'
  },
  'breath-focus': {
    id: 'breath-focus',
    icon: '🌬️',
    title: 'Breath Focus',
    description: 'Awareness of natural breathing',
    shortDescription: 'Breath'
  },
  'depth-focus': {
    id: 'depth-focus',
    icon: '🌊',
    title: 'Depth Focus',
    description: 'Deep contemplative stillness',
    shortDescription: 'Depth'
  }
};

export const DURATION_PRESETS = [5, 10, 15, 20, 30];

export const DEFAULT_SETTINGS = {
  optInReflectionAnalysis: false,
  preferredGuidanceType: 'breath-focus',
  preferredTTSVoice: 'nova',
  defaultMeditationDuration: 10,
  showGuidanceText: true
};

export const QUESTION_CATEGORIES = [
  { id: 'self', label: 'Self', icon: '🪞' },
  { id: 'relationships', label: 'Relationships', icon: '🤝' },
  { id: 'purpose', label: 'Purpose', icon: '🎯' },
  { id: 'presence', label: 'Presence', icon: '🌸' },
  { id: 'gratitude', label: 'Gratitude', icon: '🙏' }
];

export const QUESTION_DEPTHS = [
  { id: 'gentle', label: 'Gentle' },
  { id: 'moderate', label: 'Moderate' },
  { id: 'deep', label: 'Deep' }
];
```

---

## 8. App.js Updates

```javascript
// App.js (add CompanionProvider)

import { CompanionProvider } from './src/contexts/CompanionContext';

export default function App() {
  return (
    <AuthProvider>
      <NetworkProvider>
        <QuoteProvider>
          <CompanionProvider>  {/* Add this */}
            <NavigationContainer>
              <AppNavigator />
            </NavigationContainer>
          </CompanionProvider>
        </QuoteProvider>
      </NetworkProvider>
    </AuthProvider>
  );
}
```

---

## 9. Styling Guidelines

### Color Usage for Companion

| Element | Color | Hex |
|---------|-------|-----|
| Screen background | background | #EBE0D5 |
| Card background | card | #F5EEE6 |
| Response bubble | Slightly darker | #EDE4DA |
| Primary text | text | #2C1810 |
| Secondary text | textSecondary | #5D4E47 |
| Active/Selected | primary | #4E342E |
| Icons | secondary | #795548 |

### Typography for Companion

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Screen title | Serif | 28px | Bold |
| Card title | Serif | 20px | SemiBold |
| Card description | Serif | 16px | Regular |
| Response text | Serif | 17px | Regular |
| Guidance text | Serif Italic | 18px | Regular |
| Timer display | Sans | 48px | Light |
| Button text | Sans | 16px | SemiBold |

### Spacing

| Element | Spacing |
|---------|---------|
| Screen padding | 20px |
| Card padding | 24px |
| Card margin bottom | 16px |
| Section margin | 32px |
| Element gap | 12px |
