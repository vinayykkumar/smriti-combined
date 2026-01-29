# AI Reflection Companion - Frontend Implementation Plan

## Document Info
- **Feature**: AI Reflection Companion
- **Phase**: Frontend Implementation Plan
- **Created**: 2026-01-28
- **Status**: Complete

---

## 1. Implementation Order

```
Phase 1: Foundation
├── 1.1 Install Dependencies
├── 1.2 Add Constants
├── 1.3 Create API Service
└── 1.4 Create Audio Service

Phase 2: State Management
├── 2.1 CompanionContext
├── 2.2 useCompanion Hook
├── 2.3 useMeditation Hook
└── 2.4 useAudio Hook

Phase 3: Components
├── 3.1 Common Components
├── 3.2 Companion Components
└── 3.3 Meditation Components

Phase 4: Screens
├── 4.1 CompanionScreen
├── 4.2 MeditationScreen
└── 4.3 CompanionSettingsScreen

Phase 5: Navigation
├── 5.1 CompanionStackNavigator
├── 5.2 Update Tab Navigator
└── 5.3 Update App.js

Phase 6: Assets & Polish
├── 6.1 Add Audio Assets
├── 6.2 Update App Configuration
└── 6.3 Testing
```

---

## 2. Phase 1: Foundation

### 2.1 Install Dependencies

```bash
cd smriti-frontend

# Audio playback (check if already installed with Expo)
npx expo install expo-av

# Keep screen awake during meditation
npx expo install expo-keep-awake

# SVG for progress ring (if not installed)
npx expo install react-native-svg
```

### 2.2 Add Constants

**File**: `src/constants/companion.js`

```javascript
// Guidance types for meditation
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

// Duration presets in minutes
export const DURATION_PRESETS = [5, 10, 15, 20, 30];

// Default settings
export const DEFAULT_COMPANION_SETTINGS = {
  optInReflectionAnalysis: false,
  preferredGuidanceType: 'breath-focus',
  preferredTTSVoice: 'nova',
  defaultMeditationDuration: 10,
  showGuidanceText: true
};

// Question categories
export const QUESTION_CATEGORIES = [
  { id: 'self', label: 'Self', icon: '🪞' },
  { id: 'relationships', label: 'Relationships', icon: '🤝' },
  { id: 'purpose', label: 'Purpose', icon: '🎯' },
  { id: 'presence', label: 'Presence', icon: '🌸' },
  { id: 'gratitude', label: 'Gratitude', icon: '🙏' }
];

// Question depths
export const QUESTION_DEPTHS = [
  { id: 'gentle', label: 'Gentle' },
  { id: 'moderate', label: 'Moderate' },
  { id: 'deep', label: 'Deep' }
];

// Meditation session states
export const MEDITATION_STATES = {
  IDLE: 'idle',
  PREPARING: 'preparing',
  RUNNING: 'running',
  PAUSED: 'paused',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled'
};

// Mood options for reflection prompts
export const MOOD_OPTIONS = [
  { id: 'peaceful', label: 'Peaceful', icon: '☮️' },
  { id: 'contemplative', label: 'Contemplative', icon: '🤔' },
  { id: 'seeking', label: 'Seeking', icon: '🔍' },
  { id: 'grateful', label: 'Grateful', icon: '🙏' }
];
```

### 2.3 Create API Service

**File**: `src/services/api/companion.js`

```javascript
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
 * @param {Object} updates - Settings to update
 */
export const updateSettings = async (updates) => {
  const response = await apiClient.put('/companion/settings', updates);
  return response.data.data;
};

/**
 * Get personalized reflection prompt
 * @param {Object} options - { context, mood }
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
 * @param {Object} options - { category, depth }
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
 * @param {Object} options - { duration_minutes, guidance_type, include_intervals, interval_minutes }
 */
export const getMeditationGuidance = async (options) => {
  const response = await apiClient.post('/companion/meditation', {
    duration_minutes: options.durationMinutes,
    guidance_type: options.guidanceType,
    include_intervals: options.includeIntervals ?? true,
    interval_minutes: options.intervalMinutes ?? 5
  });
  return response.data.data;
};

/**
 * Text to speech - returns audio blob
 * @param {Object} options - { text, voice }
 */
export const textToSpeech = async (options) => {
  const response = await apiClient.post('/companion/tts', {
    text: options.text,
    voice: options.voice || null
  }, {
    responseType: 'arraybuffer'
  });

  // Convert to blob
  return new Blob([response.data], { type: 'audio/mpeg' });
};
```

### 2.4 Create Audio Service

**File**: `src/services/audioService.js`

```javascript
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';

// Import bell sound
const TIBETAN_BOWL = require('../assets/audio/bells/tibetan-bowl.mp3');

class AudioService {
  constructor() {
    this.bellSound = null;
    this.ttsSound = null;
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;

    try {
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        staysActiveInBackground: true,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false
      });
      this.initialized = true;
    } catch (error) {
      console.error('Failed to initialize audio:', error);
    }
  }

  async playBell() {
    await this.initialize();

    try {
      // Unload previous bell if any
      if (this.bellSound) {
        await this.bellSound.unloadAsync();
        this.bellSound = null;
      }

      const { sound } = await Audio.Sound.createAsync(
        TIBETAN_BOWL,
        { shouldPlay: true, volume: 0.8 }
      );

      this.bellSound = sound;

      // Auto-unload when done
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.didJustFinish && !status.isLooping) {
          sound.unloadAsync();
          this.bellSound = null;
        }
      });

      return sound;
    } catch (error) {
      console.error('Bell playback error:', error);
      throw error;
    }
  }

  async playTTS(audioBlob) {
    await this.initialize();

    try {
      // Unload previous TTS if any
      if (this.ttsSound) {
        await this.ttsSound.unloadAsync();
        this.ttsSound = null;
      }

      // Save blob to temp file
      const fileUri = `${FileSystem.cacheDirectory}tts_${Date.now()}.mp3`;

      // Convert blob to base64
      const reader = new FileReader();
      const base64Promise = new Promise((resolve, reject) => {
        reader.onloadend = () => {
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(audioBlob);
      });

      const base64Data = await base64Promise;
      await FileSystem.writeAsStringAsync(fileUri, base64Data, {
        encoding: FileSystem.EncodingType.Base64
      });

      // Play the audio
      const { sound } = await Audio.Sound.createAsync(
        { uri: fileUri },
        { shouldPlay: true, volume: 1.0 }
      );

      this.ttsSound = sound;

      // Return promise that resolves when playback completes
      return new Promise((resolve, reject) => {
        sound.setOnPlaybackStatusUpdate((status) => {
          if (status.didJustFinish && !status.isLooping) {
            sound.unloadAsync().then(() => {
              this.ttsSound = null;
              // Clean up temp file
              FileSystem.deleteAsync(fileUri, { idempotent: true });
              resolve();
            });
          }
          if (status.error) {
            reject(new Error(status.error));
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
    const promises = [];

    if (this.bellSound) {
      promises.push(
        this.bellSound.stopAsync()
          .then(() => this.bellSound.unloadAsync())
          .then(() => { this.bellSound = null; })
          .catch(() => {})
      );
    }

    if (this.ttsSound) {
      promises.push(
        this.ttsSound.stopAsync()
          .then(() => this.ttsSound.unloadAsync())
          .then(() => { this.ttsSound = null; })
          .catch(() => {})
      );
    }

    await Promise.all(promises);
  }

  async setVolume(volume) {
    if (this.ttsSound) {
      await this.ttsSound.setVolumeAsync(volume);
    }
  }
}

export const audioService = new AudioService();
```

---

## 3. Phase 2: State Management

### 3.1 CompanionContext

**File**: `src/contexts/CompanionContext.js`

```javascript
import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import * as companionApi from '../services/api/companion';
import { DEFAULT_COMPANION_SETTINGS } from '../constants/companion';

const CompanionContext = createContext(null);

const initialState = {
  // Settings
  settings: {
    ...DEFAULT_COMPANION_SETTINGS,
    settingsLoaded: false
  },

  // Current response
  response: {
    text: null,
    type: null, // 'prompt' | 'question' | null
    themes: [],
    basedOnReflections: false,
    followUps: []
  },

  // Loading states
  isLoading: false,
  error: null,

  // TTS state
  tts: {
    isPlaying: false,
    isLoading: false
  }
};

function companionReducer(state, action) {
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
        response: initialState.response
      };

    case 'SET_TTS_STATE':
      return { ...state, tts: { ...state.tts, ...action.payload } };

    default:
      return state;
  }
}

export function CompanionProvider({ children }) {
  const [state, dispatch] = useReducer(companionReducer, initialState);

  return (
    <CompanionContext.Provider value={{ state, dispatch }}>
      {children}
    </CompanionContext.Provider>
  );
}

export function useCompanionContext() {
  const context = useContext(CompanionContext);
  if (!context) {
    throw new Error('useCompanionContext must be used within CompanionProvider');
  }
  return context;
}
```

### 3.2 useCompanion Hook

**File**: `src/hooks/useCompanion.js`

```javascript
import { useCallback } from 'react';
import { useCompanionContext } from '../contexts/CompanionContext';
import * as companionApi from '../services/api/companion';
import { audioService } from '../services/audioService';

export function useCompanion() {
  const { state, dispatch } = useCompanionContext();

  // Load settings
  const loadSettings = useCallback(async () => {
    try {
      const settings = await companionApi.getSettings();
      dispatch({ type: 'SET_SETTINGS', payload: settings });
      return settings;
    } catch (error) {
      console.error('Failed to load companion settings:', error);
      throw error;
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
          basedOnReflections: result.based_on_reflections,
          followUps: []
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
          followUps: result.follow_up_prompts || []
        }
      });
      return result;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  }, [dispatch]);

  // Play TTS for current response
  const playResponseTTS = useCallback(async () => {
    if (!state.response.text) return;

    dispatch({ type: 'SET_TTS_STATE', payload: { isLoading: true } });
    try {
      const audioBlob = await companionApi.textToSpeech({
        text: state.response.text,
        voice: state.settings.preferredTTSVoice
      });

      dispatch({ type: 'SET_TTS_STATE', payload: { isLoading: false, isPlaying: true } });
      await audioService.playTTS(audioBlob);
      dispatch({ type: 'SET_TTS_STATE', payload: { isPlaying: false } });
    } catch (error) {
      console.error('TTS playback failed:', error);
      dispatch({ type: 'SET_TTS_STATE', payload: { isLoading: false, isPlaying: false } });
    }
  }, [state.response.text, state.settings.preferredTTSVoice, dispatch]);

  // Stop TTS
  const stopTTS = useCallback(async () => {
    await audioService.stop();
    dispatch({ type: 'SET_TTS_STATE', payload: { isPlaying: false } });
  }, [dispatch]);

  // Clear response
  const clearResponse = useCallback(() => {
    dispatch({ type: 'CLEAR_RESPONSE' });
  }, [dispatch]);

  return {
    // State
    settings: state.settings,
    response: state.response,
    isLoading: state.isLoading,
    error: state.error,
    tts: state.tts,

    // Actions
    loadSettings,
    updateSettings,
    getReflectionPrompt,
    getContemplativeQuestion,
    playResponseTTS,
    stopTTS,
    clearResponse
  };
}
```

### 3.3 useMeditation Hook

**File**: `src/hooks/useMeditation.js`

```javascript
import { useReducer, useCallback, useRef, useEffect } from 'react';
import * as companionApi from '../services/api/companion';
import { audioService } from '../services/audioService';
import { MEDITATION_STATES } from '../constants/companion';

const initialState = {
  // Session config
  duration: 10, // minutes
  guidanceType: 'breath-focus',

  // Session state
  status: MEDITATION_STATES.IDLE,
  remainingSeconds: 600,

  // Guidance
  guidance: null,
  currentGuidanceText: '',

  // TTS
  ttsEnabled: true,
  ttsLoading: false,

  // Volume
  volume: 0.8,

  // Error
  error: null
};

function meditationReducer(state, action) {
  switch (action.type) {
    case 'SET_DURATION':
      return {
        ...state,
        duration: action.payload,
        remainingSeconds: action.payload * 60
      };

    case 'SET_GUIDANCE_TYPE':
      return { ...state, guidanceType: action.payload };

    case 'SET_STATUS':
      return { ...state, status: action.payload };

    case 'SET_REMAINING':
      return { ...state, remainingSeconds: action.payload };

    case 'TICK':
      return { ...state, remainingSeconds: Math.max(0, state.remainingSeconds - 1) };

    case 'SET_GUIDANCE':
      return { ...state, guidance: action.payload };

    case 'SET_CURRENT_GUIDANCE_TEXT':
      return { ...state, currentGuidanceText: action.payload };

    case 'SET_TTS_ENABLED':
      return { ...state, ttsEnabled: action.payload };

    case 'SET_TTS_LOADING':
      return { ...state, ttsLoading: action.payload };

    case 'SET_VOLUME':
      return { ...state, volume: action.payload };

    case 'SET_ERROR':
      return { ...state, error: action.payload, status: MEDITATION_STATES.IDLE };

    case 'RESET':
      return {
        ...initialState,
        duration: state.duration,
        guidanceType: state.guidanceType,
        ttsEnabled: state.ttsEnabled,
        volume: state.volume
      };

    default:
      return state;
  }
}

export function useMeditation() {
  const [state, dispatch] = useReducer(meditationReducer, initialState);
  const timerRef = useRef(null);
  const guidanceTimersRef = useRef([]);

  // Configure session
  const setDuration = useCallback((minutes) => {
    dispatch({ type: 'SET_DURATION', payload: minutes });
  }, []);

  const setGuidanceType = useCallback((type) => {
    dispatch({ type: 'SET_GUIDANCE_TYPE', payload: type });
  }, []);

  const setTTSEnabled = useCallback((enabled) => {
    dispatch({ type: 'SET_TTS_ENABLED', payload: enabled });
  }, []);

  const setVolume = useCallback((volume) => {
    dispatch({ type: 'SET_VOLUME', payload: volume });
    audioService.setVolume(volume);
  }, []);

  // Play TTS for guidance text
  const playGuidanceTTS = useCallback(async (text) => {
    if (!state.ttsEnabled || !text) return;

    dispatch({ type: 'SET_TTS_LOADING', payload: true });
    try {
      const audioBlob = await companionApi.textToSpeech({ text });
      await audioService.playTTS(audioBlob);
    } catch (error) {
      console.error('TTS playback failed:', error);
    } finally {
      dispatch({ type: 'SET_TTS_LOADING', payload: false });
    }
  }, [state.ttsEnabled]);

  // Start timer
  const startTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    timerRef.current = setInterval(() => {
      dispatch({ type: 'TICK' });
    }, 1000);
  }, []);

  // Schedule interval guidance
  const scheduleIntervalGuidance = useCallback((guidance, totalSeconds) => {
    // Clear any existing timers
    guidanceTimersRef.current.forEach(t => clearTimeout(t));
    guidanceTimersRef.current = [];

    if (!guidance.intervals?.length) return;

    const intervalCount = guidance.intervals.length;
    const intervalDuration = totalSeconds / (intervalCount + 1);

    // Schedule each interval
    guidance.intervals.forEach((text, index) => {
      const timer = setTimeout(async () => {
        dispatch({ type: 'SET_CURRENT_GUIDANCE_TEXT', payload: text });
        await playGuidanceTTS(text);
      }, intervalDuration * (index + 1) * 1000);

      guidanceTimersRef.current.push(timer);
    });

    // Schedule closing guidance (1 minute before end)
    if (totalSeconds > 60) {
      const closingTimer = setTimeout(async () => {
        dispatch({ type: 'SET_CURRENT_GUIDANCE_TEXT', payload: guidance.closing });
        await playGuidanceTTS(guidance.closing);
      }, (totalSeconds - 60) * 1000);

      guidanceTimersRef.current.push(closingTimer);
    }
  }, [playGuidanceTTS]);

  // Start session
  const startSession = useCallback(async () => {
    dispatch({ type: 'SET_STATUS', payload: MEDITATION_STATES.PREPARING });
    dispatch({ type: 'SET_REMAINING', payload: state.duration * 60 });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      // Calculate interval minutes
      const intervalMinutes = Math.max(1, Math.floor(state.duration / 3));

      // Fetch guidance from AI
      const guidance = await companionApi.getMeditationGuidance({
        durationMinutes: state.duration,
        guidanceType: state.guidanceType,
        includeIntervals: true,
        intervalMinutes
      });

      dispatch({ type: 'SET_GUIDANCE', payload: guidance });

      // Play start bell
      await audioService.playBell();

      // Wait a moment for bell to ring
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Start the session
      dispatch({ type: 'SET_STATUS', payload: MEDITATION_STATES.RUNNING });

      // Show and play opening guidance
      dispatch({ type: 'SET_CURRENT_GUIDANCE_TEXT', payload: guidance.opening });
      await playGuidanceTTS(guidance.opening);

      // After opening, show settling guidance
      setTimeout(async () => {
        dispatch({ type: 'SET_CURRENT_GUIDANCE_TEXT', payload: guidance.settling });
        await playGuidanceTTS(guidance.settling);
      }, 30000); // 30 seconds in

      // Schedule interval guidance
      scheduleIntervalGuidance(guidance, state.duration * 60);

      // Start countdown
      startTimer();

    } catch (error) {
      console.error('Failed to start meditation:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to start meditation. Please try again.' });
    }
  }, [state.duration, state.guidanceType, playGuidanceTTS, scheduleIntervalGuidance, startTimer]);

  // Pause session
  const pauseSession = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    audioService.pause();
    dispatch({ type: 'SET_STATUS', payload: MEDITATION_STATES.PAUSED });
  }, []);

  // Resume session
  const resumeSession = useCallback(() => {
    dispatch({ type: 'SET_STATUS', payload: MEDITATION_STATES.RUNNING });
    startTimer();
    audioService.resume();
  }, [startTimer]);

  // End session
  const endSession = useCallback(async () => {
    // Clear timers
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    guidanceTimersRef.current.forEach(t => clearTimeout(t));
    guidanceTimersRef.current = [];

    // Stop any playing audio
    await audioService.stop();

    // Play end bell
    await audioService.playBell();

    dispatch({ type: 'SET_STATUS', payload: MEDITATION_STATES.COMPLETED });
  }, []);

  // Reset for new session
  const resetSession = useCallback(() => {
    // Clear all timers
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    guidanceTimersRef.current.forEach(t => clearTimeout(t));
    guidanceTimersRef.current = [];

    // Stop audio
    audioService.stop();

    dispatch({ type: 'RESET' });
  }, []);

  // Check for session completion
  useEffect(() => {
    if (state.status === MEDITATION_STATES.RUNNING && state.remainingSeconds <= 0) {
      endSession();
    }
  }, [state.status, state.remainingSeconds, endSession]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      guidanceTimersRef.current.forEach(t => clearTimeout(t));
      audioService.stop();
    };
  }, []);

  // Compute progress
  const progress = state.duration > 0
    ? 1 - (state.remainingSeconds / (state.duration * 60))
    : 0;

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
    error: state.error,
    progress,

    // Actions
    setDuration,
    setGuidanceType,
    setTTSEnabled,
    setVolume,
    startSession,
    pauseSession,
    resumeSession,
    endSession,
    resetSession
  };
}
```

---

## 4. Phase 3: Components

### Component Files to Create

```
src/components/
├── companion/
│   ├── CompanionCard.js
│   ├── ResponseBubble.js
│   ├── OptInBanner.js
│   └── TTSButton.js
│
└── meditation/
    ├── DurationPicker.js
    ├── GuidanceTypePicker.js
    ├── ProgressRing.js
    ├── TimerDisplay.js
    ├── GuidanceDisplay.js
    └── TimerControls.js
```

**Note**: Full component implementations are in `04-frontend-components.md`.

---

## 5. Phase 4: Screens

### Screen Files to Create

```
src/screens/companion/
├── CompanionScreen.js
├── MeditationScreen.js
└── CompanionSettingsScreen.js
```

### 5.1 CompanionScreen (Main)

**File**: `src/screens/companion/CompanionScreen.js`

```javascript
import React, { useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  Text,
  ActivityIndicator
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useCompanion } from '../../hooks/useCompanion';
import { useAuth } from '../../hooks/useAuth';
import CompanionCard from '../../components/companion/CompanionCard';
import ResponseBubble from '../../components/companion/ResponseBubble';
import OptInBanner from '../../components/companion/OptInBanner';
import theme from '../../styles/theme';

export default function CompanionScreen() {
  const navigation = useNavigation();
  const { isAuthenticated } = useAuth();
  const {
    settings,
    response,
    isLoading,
    error,
    tts,
    loadSettings,
    getReflectionPrompt,
    getContemplativeQuestion,
    playResponseTTS,
    stopTTS,
    clearResponse
  } = useCompanion();

  // Load settings on mount
  useEffect(() => {
    if (isAuthenticated && !settings.settingsLoaded) {
      loadSettings();
    }
  }, [isAuthenticated, settings.settingsLoaded, loadSettings]);

  const handleSettingsPress = () => {
    navigation.navigate('CompanionSettings');
  };

  const handleMeditationPress = () => {
    navigation.navigate('Meditation');
  };

  const handlePromptPress = async () => {
    clearResponse();
    await getReflectionPrompt();
  };

  const handleQuestionPress = async () => {
    clearResponse();
    await getContemplativeQuestion({ depth: 'moderate' });
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={handleSettingsPress} style={styles.settingsButton}>
          <Text style={styles.settingsIcon}>⚙️</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Companion</Text>
        <View style={styles.settingsButton} />
      </View>

      <ScrollView
        style={styles.content}
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={false}
      >
        {/* Opt-in Banner (if not opted in) */}
        {settings.settingsLoaded && !settings.optInReflectionAnalysis && (
          <OptInBanner />
        )}

        {/* Action Cards */}
        <CompanionCard
          icon="🪷"
          title="Reflection Prompt"
          description="Get a personalized prompt based on your journey"
          onPress={handlePromptPress}
          disabled={isLoading}
          loading={isLoading && !response.text}
        />

        <CompanionCard
          icon="💭"
          title="Contemplative Question"
          description="Explore deeper aspects of your practice"
          onPress={handleQuestionPress}
          disabled={isLoading}
          loading={isLoading && !response.text}
        />

        <CompanionCard
          icon="🧘"
          title="Guided Meditation"
          description="Sankalpam • Breath • Depth"
          onPress={handleMeditationPress}
          disabled={isLoading}
        />

        {/* Divider */}
        {response.text && <View style={styles.divider} />}

        {/* Response Section */}
        {response.text && (
          <ResponseBubble
            text={response.text}
            type={response.type}
            themes={response.themes}
            basedOnReflections={response.basedOnReflections}
            followUps={response.followUps}
            ttsPlaying={tts.isPlaying}
            ttsLoading={tts.isLoading}
            onTTSPlay={playResponseTTS}
            onTTSStop={stopTTS}
          />
        )}

        {/* Error Message */}
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* Loading Indicator */}
        {isLoading && !response.text && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color={theme.colors.primary} />
            <Text style={styles.loadingText}>Contemplating...</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md
  },
  settingsButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center'
  },
  settingsIcon: {
    fontSize: 24
  },
  title: {
    fontFamily: theme.fonts.serif,
    fontSize: theme.fontSizes.title,
    color: theme.colors.text
  },
  content: {
    flex: 1
  },
  contentContainer: {
    padding: theme.spacing.lg,
    paddingBottom: theme.spacing.xxl
  },
  divider: {
    height: 1,
    backgroundColor: theme.colors.border,
    marginVertical: theme.spacing.lg
  },
  errorContainer: {
    backgroundColor: '#FEE2E2',
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    marginTop: theme.spacing.md
  },
  errorText: {
    color: '#DC2626',
    fontFamily: theme.fonts.sans,
    fontSize: theme.fontSizes.body
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing.lg
  },
  loadingText: {
    marginLeft: theme.spacing.sm,
    fontFamily: theme.fonts.serif,
    fontSize: theme.fontSizes.body,
    color: theme.colors.textSecondary,
    fontStyle: 'italic'
  }
});
```

---

## 6. Phase 5: Navigation

### 6.1 CompanionStackNavigator

**File**: `src/navigation/CompanionStackNavigator.js`

```javascript
import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import CompanionScreen from '../screens/companion/CompanionScreen';
import MeditationScreen from '../screens/companion/MeditationScreen';
import CompanionSettingsScreen from '../screens/companion/CompanionSettingsScreen';
import theme from '../styles/theme';

const Stack = createNativeStackNavigator();

export default function CompanionStackNavigator() {
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
}
```

### 6.2 Update Tab Navigator

**File**: `src/navigation/AppNavigator.js` (update)

Add the Companion tab to the bottom tab navigator. See `04-frontend-components.md` Section 6 for details.

### 6.3 Update App.js

**File**: `App.js` (update)

```javascript
// Add import
import { CompanionProvider } from './src/contexts/CompanionContext';

// Wrap in provider
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

## 7. Phase 6: Assets & Polish

### 7.1 Add Audio Assets

**Directory**: `src/assets/audio/bells/`

Add the tibetan bowl sound file:
- `tibetan-bowl.mp3` - High quality tibetan singing bowl sound

**Sources for royalty-free sounds**:
- Freesound.org
- Pixabay
- ZapSplat

### 7.2 Update App Configuration

**File**: `app.json` (updates for background audio)

```json
{
  "expo": {
    "ios": {
      "infoPlist": {
        "UIBackgroundModes": ["audio"]
      }
    },
    "android": {
      "permissions": [
        "android.permission.FOREGROUND_SERVICE"
      ]
    }
  }
}
```

---

## 8. File Checklist

### New Files to Create

```
src/
├── constants/
│   └── companion.js                    ☐
│
├── services/
│   ├── api/
│   │   └── companion.js                ☐
│   └── audioService.js                 ☐
│
├── contexts/
│   └── CompanionContext.js             ☐
│
├── hooks/
│   ├── useCompanion.js                 ☐
│   └── useMeditation.js                ☐
│
├── components/
│   ├── companion/
│   │   ├── CompanionCard.js            ☐
│   │   ├── ResponseBubble.js           ☐
│   │   ├── OptInBanner.js              ☐
│   │   └── TTSButton.js                ☐
│   │
│   └── meditation/
│       ├── DurationPicker.js           ☐
│       ├── GuidanceTypePicker.js       ☐
│       ├── ProgressRing.js             ☐
│       ├── TimerDisplay.js             ☐
│       ├── GuidanceDisplay.js          ☐
│       └── TimerControls.js            ☐
│
├── screens/
│   └── companion/
│       ├── CompanionScreen.js          ☐
│       ├── MeditationScreen.js         ☐
│       └── CompanionSettingsScreen.js  ☐
│
├── navigation/
│   └── CompanionStackNavigator.js      ☐
│
└── assets/
    └── audio/
        └── bells/
            └── tibetan-bowl.mp3        ☐
```

### Files to Modify

```
src/
├── navigation/
│   └── AppNavigator.js                 ☐ (add Companion tab)
│
├── App.js                              ☐ (add CompanionProvider)
│
└── app.json                            ☐ (add background audio config)
```

---

## 9. Testing Checklist

### Component Tests
- [ ] CompanionCard renders correctly
- [ ] ResponseBubble displays text
- [ ] ProgressRing animates
- [ ] TimerControls change state

### Hook Tests
- [ ] useCompanion loads settings
- [ ] useCompanion fetches prompts
- [ ] useMeditation timer works
- [ ] useMeditation state transitions

### Integration Tests
- [ ] Companion tab appears
- [ ] Navigation works between screens
- [ ] API calls succeed
- [ ] Audio playback works
- [ ] TTS playback works

### Manual Testing
- [ ] Request reflection prompt
- [ ] Request contemplative question
- [ ] Start meditation session
- [ ] Pause and resume meditation
- [ ] End meditation early
- [ ] Complete full meditation
- [ ] TTS plays correctly
- [ ] Bell sounds play
- [ ] Settings update correctly
- [ ] Opt-in toggle works
