import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Platform,
  RefreshControl,
  Modal,
  Animated,
  Easing,
  FlatList,
  Alert,
  TextInput,
  KeyboardAvoidingView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../styles/theme';
import { useCompanion } from '../hooks/useCompanion';

// Category options for contemplative questions
const QUESTION_CATEGORIES = [
  { id: 'self', label: 'Self', icon: 'person-outline', description: 'Know thyself' },
  { id: 'relationships', label: 'Relationships', icon: 'heart-outline', description: 'Connection with others' },
  { id: 'purpose', label: 'Purpose', icon: 'compass-outline', description: 'Life direction' },
  { id: 'presence', label: 'Presence', icon: 'leaf-outline', description: 'Being here now' },
  { id: 'gratitude', label: 'Gratitude', icon: 'sunny-outline', description: 'Appreciation' },
];

// Depth levels for questions
const DEPTH_LEVELS = [
  { id: 'gentle', label: 'Gentle', description: 'Light reflection' },
  { id: 'moderate', label: 'Moderate', description: 'Deeper inquiry' },
  { id: 'deep', label: 'Deep', description: 'Profound exploration' },
];

// Mood options for reflection prompts
const MOOD_OPTIONS = [
  { id: 'calm', label: 'Calm', icon: 'water-outline' },
  { id: 'anxious', label: 'Unsettled', icon: 'cloudy-outline' },
  { id: 'grateful', label: 'Grateful', icon: 'heart-outline' },
  { id: 'reflective', label: 'Reflective', icon: 'moon-outline' },
  { id: 'seeking', label: 'Seeking', icon: 'search-outline' },
];

// Meditation types
const MEDITATION_TYPES = [
  {
    id: 'sankalpam',
    label: 'Sankalpam',
    description: 'Set a sacred intention for your practice',
    icon: 'flame-outline',
    color: '#E57373'
  },
  {
    id: 'breath-focus',
    label: 'Breath Awareness',
    description: 'Simple presence with the breath',
    icon: 'leaf-outline',
    color: '#81C784'
  },
  {
    id: 'depth-focus',
    label: 'Deep Contemplation',
    description: 'Journey into inner stillness',
    icon: 'water-outline',
    color: '#64B5F6'
  },
];

// Spiritual loading messages
const LOADING_MESSAGES = {
  prompt: [
    'Listening to your inner landscape...',
    'Gathering wisdom from stillness...',
    'Crafting your reflection...',
    'Finding the right words...',
  ],
  question: [
    'Seeking a meaningful inquiry...',
    'Contemplating your path...',
    'Finding the right question...',
    'Listening deeply...',
  ],
  meditation: [
    'Preparing sacred space...',
    'Gathering guidance...',
    'Creating your sanctuary...',
    'Tuning into peace...',
  ],
};

// Breathing animation component
const BreathingOrb = ({ style }) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const opacityAnim = useRef(new Animated.Value(0.6)).current;

  useEffect(() => {
    const breatheIn = Animated.parallel([
      Animated.timing(scaleAnim, {
        toValue: 1.3,
        duration: 4000,
        easing: Easing.inOut(Easing.ease),
        useNativeDriver: true,
      }),
      Animated.timing(opacityAnim, {
        toValue: 1,
        duration: 4000,
        easing: Easing.inOut(Easing.ease),
        useNativeDriver: true,
      }),
    ]);

    const breatheOut = Animated.parallel([
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 4000,
        easing: Easing.inOut(Easing.ease),
        useNativeDriver: true,
      }),
      Animated.timing(opacityAnim, {
        toValue: 0.6,
        duration: 4000,
        easing: Easing.inOut(Easing.ease),
        useNativeDriver: true,
      }),
    ]);

    const loop = Animated.loop(
      Animated.sequence([breatheIn, breatheOut])
    );
    loop.start();

    return () => loop.stop();
  }, []);

  return (
    <Animated.View
      style={[
        styles.breathingOrb,
        style,
        {
          transform: [{ scale: scaleAnim }],
          opacity: opacityAnim,
        },
      ]}
    />
  );
};

// Fade-in animation wrapper
const FadeIn = ({ children, delay = 0, style }) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        delay,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: 0,
        duration: 600,
        delay,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  return (
    <Animated.View
      style={[
        style,
        {
          opacity: fadeAnim,
          transform: [{ translateY }],
        },
      ]}
    >
      {children}
    </Animated.View>
  );
};

export default function AICompanionScreen({ navigation }) {
  const {
    generating,
    currentContent,
    contentType,
    generatePrompt,
    generateQuestion,
    generateMeditation,
    clearContent,
    error,
    clearError,
    // History
    history,
    historyLoading,
    hasMoreHistory,
    loadHistory,
    deleteHistoryEntry,
    clearHistory,
  } = useCompanion();

  // Tab state
  const [activeTab, setActiveTab] = useState('prompt');

  // Prompt options
  const [selectedMood, setSelectedMood] = useState(null);

  // Question options
  const [selectedCategory, setSelectedCategory] = useState('self');
  const [selectedDepth, setSelectedDepth] = useState('moderate');

  // Meditation options
  const [selectedMeditationType, setSelectedMeditationType] = useState('breath-focus');
  const [meditationDuration, setMeditationDuration] = useState(10);
  const [intention, setIntention] = useState('');

  // UI state
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [showMeditationModal, setShowMeditationModal] = useState(false);
  const [historyPage, setHistoryPage] = useState(1);
  const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);

  // Rotate loading messages
  useEffect(() => {
    if (generating) {
      const messages = LOADING_MESSAGES[activeTab] || LOADING_MESSAGES.prompt;
      let index = 0;
      setLoadingMessage(messages[0]);

      const interval = setInterval(() => {
        index = (index + 1) % messages.length;
        setLoadingMessage(messages[index]);
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [generating, activeTab]);

  // Load history when switching to history tab
  useEffect(() => {
    if (activeTab === 'history') {
      loadHistory(1);
      setHistoryPage(1);
    }
  }, [activeTab]);

  // Clear content when switching tabs (except history)
  useEffect(() => {
    if (activeTab !== 'history') {
      clearContent();
      clearError();
    }
  }, [activeTab]);

  const handleGenerate = useCallback(async () => {
    clearError();

    switch (activeTab) {
      case 'prompt':
        await generatePrompt({ mood: selectedMood });
        break;
      case 'question':
        await generateQuestion({
          category: selectedCategory,
          depth: selectedDepth
        });
        break;
      case 'meditation':
        await generateMeditation({
          guidanceType: selectedMeditationType,
          durationMinutes: meditationDuration,
          intention: intention.trim() || null,
        });
        break;
    }
  }, [activeTab, selectedMood, selectedCategory, selectedDepth, selectedMeditationType, meditationDuration, intention]);

  const handleLoadMoreHistory = useCallback(() => {
    if (!historyLoading && hasMoreHistory) {
      const nextPage = historyPage + 1;
      setHistoryPage(nextPage);
      loadHistory(nextPage);
    }
  }, [historyLoading, hasMoreHistory, historyPage]);

  const handleDeleteHistoryItem = useCallback((item) => {
    Alert.alert(
      'Delete Entry',
      'Remove this from your history?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => deleteHistoryEntry(item._id),
        },
      ]
    );
  }, [deleteHistoryEntry]);

  const handleClearAllHistory = useCallback(() => {
    Alert.alert(
      'Clear All History',
      'This will remove all your past interactions. This cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear All',
          style: 'destructive',
          onPress: clearHistory,
        },
      ]
    );
  }, [clearHistory]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    if (activeTab === 'history') {
      await loadHistory(1);
      setHistoryPage(1);
    } else {
      clearContent();
      await handleGenerate();
    }
    setRefreshing(false);
  }, [activeTab, handleGenerate]);

  // ============ RENDER FUNCTIONS ============

  const renderTabBar = () => (
    <View style={styles.tabBar}>
      {[
        { id: 'prompt', label: 'Reflect', icon: 'sparkles-outline' },
        { id: 'question', label: 'Contemplate', icon: 'help-circle-outline' },
        { id: 'meditation', label: 'Meditate', icon: 'leaf-outline' },
        { id: 'history', label: 'History', icon: 'time-outline' },
      ].map((tab) => (
        <TouchableOpacity
          key={tab.id}
          style={[styles.tab, activeTab === tab.id && styles.activeTab]}
          onPress={() => setActiveTab(tab.id)}
        >
          <Ionicons
            name={tab.icon}
            size={18}
            color={activeTab === tab.id ? COLORS.primary : COLORS.textLight}
          />
          <Text style={[styles.tabText, activeTab === tab.id && styles.activeTabText]}>
            {tab.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderPromptOptions = () => (
    <FadeIn style={styles.optionsContainer}>
      <Text style={styles.sectionIntro}>
        Take a moment to check in with yourself. How are you feeling right now?
      </Text>

      <Text style={styles.optionLabel}>Current State</Text>
      <View style={styles.optionChips}>
        {MOOD_OPTIONS.map((mood) => (
          <TouchableOpacity
            key={mood.id}
            style={[
              styles.chip,
              selectedMood === mood.id && styles.chipSelected,
            ]}
            onPress={() => setSelectedMood(selectedMood === mood.id ? null : mood.id)}
          >
            <Ionicons
              name={mood.icon}
              size={16}
              color={selectedMood === mood.id ? COLORS.white : COLORS.secondary}
            />
            <Text
              style={[
                styles.chipText,
                selectedMood === mood.id && styles.chipTextSelected,
              ]}
            >
              {mood.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.optionHint}>
        {selectedMood
          ? 'Your prompt will be personalized to meet you where you are.'
          : 'Select a mood for a more personalized prompt, or leave empty for a general reflection.'}
      </Text>
    </FadeIn>
  );

  const renderQuestionOptions = () => (
    <FadeIn style={styles.optionsContainer}>
      <Text style={styles.sectionIntro}>
        What aspect of life would you like to explore today?
      </Text>

      <Text style={styles.optionLabel}>Theme</Text>
      <View style={styles.categoryGrid}>
        {QUESTION_CATEGORIES.map((category) => (
          <TouchableOpacity
            key={category.id}
            style={[
              styles.categoryCard,
              selectedCategory === category.id && styles.categoryCardSelected,
            ]}
            onPress={() => setSelectedCategory(category.id)}
          >
            <Ionicons
              name={category.icon}
              size={24}
              color={selectedCategory === category.id ? COLORS.primary : COLORS.secondary}
            />
            <Text
              style={[
                styles.categoryLabel,
                selectedCategory === category.id && styles.categoryLabelSelected,
              ]}
            >
              {category.label}
            </Text>
            <Text style={styles.categoryDesc}>{category.description}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={[styles.optionLabel, { marginTop: SPACING.lg }]}>Depth</Text>
      <View style={styles.depthSelector}>
        {DEPTH_LEVELS.map((depth) => (
          <TouchableOpacity
            key={depth.id}
            style={[
              styles.depthChip,
              selectedDepth === depth.id && styles.depthChipSelected,
            ]}
            onPress={() => setSelectedDepth(depth.id)}
          >
            <Text
              style={[
                styles.depthText,
                selectedDepth === depth.id && styles.depthTextSelected,
              ]}
            >
              {depth.label}
            </Text>
            <Text
              style={[
                styles.depthDesc,
                selectedDepth === depth.id && styles.depthDescSelected,
              ]}
            >
              {depth.description}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </FadeIn>
  );

  const renderMeditationOptions = () => (
    <FadeIn style={styles.optionsContainer}>
      <Text style={styles.sectionIntro}>
        Create a moment of stillness. Choose your practice and duration.
      </Text>

      <Text style={styles.optionLabel}>Practice Type</Text>
      <View style={styles.meditationTypes}>
        {MEDITATION_TYPES.map((type) => (
          <TouchableOpacity
            key={type.id}
            style={[
              styles.meditationCard,
              selectedMeditationType === type.id && styles.meditationCardSelected,
            ]}
            onPress={() => setSelectedMeditationType(type.id)}
          >
            <View style={[styles.meditationIconWrap, { backgroundColor: type.color + '20' }]}>
              <Ionicons name={type.icon} size={24} color={type.color} />
            </View>
            <View style={styles.meditationCardContent}>
              <Text
                style={[
                  styles.meditationCardTitle,
                  selectedMeditationType === type.id && styles.meditationCardTitleSelected,
                ]}
              >
                {type.label}
              </Text>
              <Text style={styles.meditationCardDesc}>{type.description}</Text>
            </View>
            {selectedMeditationType === type.id && (
              <Ionicons name="checkmark-circle" size={20} color={COLORS.accent} />
            )}
          </TouchableOpacity>
        ))}
      </View>

      <Text style={[styles.optionLabel, { marginTop: SPACING.lg }]}>Duration</Text>
      <View style={styles.durationSelector}>
        {[5, 10, 15, 20].map((mins) => (
          <TouchableOpacity
            key={mins}
            style={[
              styles.durationChip,
              meditationDuration === mins && styles.durationChipSelected,
            ]}
            onPress={() => setMeditationDuration(mins)}
          >
            <Text
              style={[
                styles.durationNumber,
                meditationDuration === mins && styles.durationNumberSelected,
              ]}
            >
              {mins}
            </Text>
            <Text
              style={[
                styles.durationLabel,
                meditationDuration === mins && styles.durationLabelSelected,
              ]}
            >
              min
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {selectedMeditationType === 'sankalpam' && (
        <View style={styles.intentionContainer}>
          <Text style={styles.optionLabel}>Your Intention (Optional)</Text>
          <TextInput
            style={styles.intentionInput}
            placeholder="What intention would you like to set?"
            placeholderTextColor={COLORS.textLight}
            value={intention}
            onChangeText={setIntention}
            multiline
            numberOfLines={2}
            maxLength={200}
          />
        </View>
      )}
    </FadeIn>
  );

  const renderLoadingState = () => (
    <View style={styles.loadingContainer}>
      <BreathingOrb />
      <Text style={styles.loadingText}>{loadingMessage}</Text>
      <Text style={styles.loadingHint}>Breathe gently as you wait...</Text>
    </View>
  );

  const renderErrorState = () => (
    <FadeIn style={styles.errorContainer}>
      <View style={styles.errorIconWrap}>
        <Ionicons name="cloud-offline-outline" size={48} color={COLORS.textLight} />
      </View>
      <Text style={styles.errorTitle}>A moment of stillness...</Text>
      <Text style={styles.errorText}>
        {error || 'Something interrupted our connection. Please try again when you are ready.'}
      </Text>
      <TouchableOpacity style={styles.retryButton} onPress={handleGenerate}>
        <Ionicons name="refresh-outline" size={18} color={COLORS.accent} />
        <Text style={styles.retryButtonText}>Try Again</Text>
      </TouchableOpacity>
    </FadeIn>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <View style={styles.emptyIconWrap}>
        <Ionicons
          name={
            activeTab === 'prompt'
              ? 'sparkles'
              : activeTab === 'question'
              ? 'help-circle'
              : 'leaf'
          }
          size={40}
          color={COLORS.accent}
        />
      </View>
      <Text style={styles.emptyTitle}>
        {activeTab === 'prompt' && 'Begin Your Reflection'}
        {activeTab === 'question' && 'Seek Inner Wisdom'}
        {activeTab === 'meditation' && 'Find Your Stillness'}
      </Text>
      <Text style={styles.emptySubtitle}>
        {activeTab === 'prompt' && 'Receive a prompt to guide your inner exploration'}
        {activeTab === 'question' && 'Discover a question to illuminate your path'}
        {activeTab === 'meditation' && 'Let guidance lead you into peaceful presence'}
      </Text>
    </View>
  );

  const renderPromptContent = () => (
    <FadeIn style={styles.contentCard}>
      <View style={styles.contentIconWrap}>
        <Ionicons name="sparkles" size={24} color={COLORS.accent} />
      </View>
      <Text style={styles.contentLabel}>For Your Reflection</Text>
      <Text style={styles.promptText}>{currentContent.prompt}</Text>
      {currentContent.theme && (
        <View style={styles.contentMeta}>
          <Ionicons name="bookmark-outline" size={14} color={COLORS.textLight} />
          <Text style={styles.metaText}>{currentContent.theme}</Text>
        </View>
      )}
      <Text style={styles.contentInvitation}>
        Sit with this prompt. Let it settle. There is no rush.
      </Text>
    </FadeIn>
  );

  const renderQuestionContent = () => (
    <FadeIn style={styles.contentCard}>
      <View style={styles.contentIconWrap}>
        <Ionicons name="help-circle" size={24} color={COLORS.accent} />
      </View>
      <Text style={styles.contentLabel}>Contemplate</Text>
      <Text style={styles.questionText}>{currentContent.question}</Text>

      {currentContent.follow_up_prompts && currentContent.follow_up_prompts.length > 0 && (
        <View style={styles.followUps}>
          <Text style={styles.followUpsLabel}>To go deeper...</Text>
          {currentContent.follow_up_prompts.map((followUp, index) => (
            <View key={index} style={styles.followUpItem}>
              <View style={styles.followUpDot} />
              <Text style={styles.followUpText}>{followUp}</Text>
            </View>
          ))}
        </View>
      )}

      <Text style={styles.contentInvitation}>
        Let the question guide you inward. The answer lives within.
      </Text>
    </FadeIn>
  );

  const renderMeditationContent = () => (
    <FadeIn style={styles.contentCard}>
      <View style={styles.contentIconWrap}>
        <Ionicons name="leaf" size={24} color={COLORS.accent} />
      </View>
      <Text style={styles.contentLabel}>Your Guidance</Text>

      <View style={styles.meditationPreview}>
        <Text style={styles.meditationPreviewTitle}>Opening</Text>
        <Text style={styles.meditationPreviewText} numberOfLines={3}>
          {currentContent.opening}
        </Text>
      </View>

      <TouchableOpacity
        style={styles.viewFullButton}
        onPress={() => setShowMeditationModal(true)}
      >
        <Text style={styles.viewFullButtonText}>View Full Guidance</Text>
        <Ionicons name="expand-outline" size={18} color={COLORS.accent} />
      </TouchableOpacity>

      <Text style={styles.contentInvitation}>
        Find a comfortable position. Close your eyes when ready.
      </Text>
    </FadeIn>
  );

  const renderMeditationModal = () => (
    <Modal
      visible={showMeditationModal}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setShowMeditationModal(false)}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Meditation Guidance</Text>
          <TouchableOpacity
            style={styles.modalCloseButton}
            onPress={() => setShowMeditationModal(false)}
          >
            <Ionicons name="close" size={24} color={COLORS.primary} />
          </TouchableOpacity>
        </View>

        <ScrollView
          style={styles.modalScroll}
          contentContainerStyle={styles.modalContent}
          showsVerticalScrollIndicator={false}
        >
          {currentContent && (
            <>
              <View style={styles.meditationFullSection}>
                <View style={styles.sectionIconRow}>
                  <View style={[styles.sectionIcon, { backgroundColor: '#E8F5E9' }]}>
                    <Ionicons name="sunny-outline" size={20} color="#66BB6A" />
                  </View>
                  <Text style={styles.meditationSectionTitle}>Opening</Text>
                </View>
                <Text style={styles.meditationFullText}>{currentContent.opening}</Text>
              </View>

              <View style={styles.meditationFullSection}>
                <View style={styles.sectionIconRow}>
                  <View style={[styles.sectionIcon, { backgroundColor: '#E3F2FD' }]}>
                    <Ionicons name="water-outline" size={20} color="#42A5F5" />
                  </View>
                  <Text style={styles.meditationSectionTitle}>Settling In</Text>
                </View>
                <Text style={styles.meditationFullText}>{currentContent.settling}</Text>
              </View>

              {currentContent.intervals && currentContent.intervals.length > 0 && (
                <View style={styles.meditationFullSection}>
                  <View style={styles.sectionIconRow}>
                    <View style={[styles.sectionIcon, { backgroundColor: '#FFF3E0' }]}>
                      <Ionicons name="infinite-outline" size={20} color="#FFA726" />
                    </View>
                    <Text style={styles.meditationSectionTitle}>Guidance</Text>
                  </View>
                  {currentContent.intervals.map((interval, index) => (
                    <View key={index} style={styles.intervalBlock}>
                      <Text style={styles.meditationFullText}>{interval}</Text>
                      {index < currentContent.intervals.length - 1 && (
                        <View style={styles.intervalDivider}>
                          <Ionicons name="ellipsis-horizontal" size={20} color={COLORS.border} />
                        </View>
                      )}
                    </View>
                  ))}
                </View>
              )}

              <View style={styles.meditationFullSection}>
                <View style={styles.sectionIconRow}>
                  <View style={[styles.sectionIcon, { backgroundColor: '#F3E5F5' }]}>
                    <Ionicons name="moon-outline" size={20} color="#AB47BC" />
                  </View>
                  <Text style={styles.meditationSectionTitle}>Closing</Text>
                </View>
                <Text style={styles.meditationFullText}>{currentContent.closing}</Text>
              </View>

              <View style={styles.meditationClosing}>
                <Ionicons name="heart-outline" size={24} color={COLORS.accent} />
                <Text style={styles.meditationClosingText}>
                  May this practice bring you peace
                </Text>
              </View>
            </>
          )}
        </ScrollView>
      </View>
    </Modal>
  );

  const renderContent = () => {
    if (generating) return renderLoadingState();
    if (error) return renderErrorState();
    if (!currentContent) return renderEmptyState();

    switch (contentType) {
      case 'prompt':
        return renderPromptContent();
      case 'question':
        return renderQuestionContent();
      case 'meditation':
        return renderMeditationContent();
      default:
        return renderEmptyState();
    }
  };

  // ============ HISTORY RENDERING ============

  const renderHistoryItem = ({ item }) => {
    const typeConfig = {
      prompt: { icon: 'sparkles', color: '#FFB74D', label: 'Reflection' },
      contemplate: { icon: 'help-circle', color: '#64B5F6', label: 'Question' },
      meditation: { icon: 'leaf', color: '#81C784', label: 'Meditation' },
    };

    const config = typeConfig[item.type] || typeConfig.prompt;
    const date = new Date(item.created_at);
    const timeAgo = getTimeAgo(date);

    return (
      <TouchableOpacity
        style={styles.historyItem}
        onPress={() => setSelectedHistoryItem(item)}
        onLongPress={() => handleDeleteHistoryItem(item)}
      >
        <View style={[styles.historyIconWrap, { backgroundColor: config.color + '20' }]}>
          <Ionicons name={config.icon} size={20} color={config.color} />
        </View>
        <View style={styles.historyContent}>
          <Text style={styles.historyType}>{config.label}</Text>
          <Text style={styles.historyPreview} numberOfLines={2}>
            {item.response?.prompt || item.response?.question || item.response?.opening || 'No content'}
          </Text>
          <Text style={styles.historyTime}>{timeAgo}</Text>
        </View>
        <Ionicons name="chevron-forward" size={18} color={COLORS.border} />
      </TouchableOpacity>
    );
  };

  const renderHistoryTab = () => (
    <View style={styles.historyContainer}>
      {history.length > 0 && (
        <TouchableOpacity style={styles.clearAllButton} onPress={handleClearAllHistory}>
          <Ionicons name="trash-outline" size={16} color={COLORS.error} />
          <Text style={styles.clearAllText}>Clear All</Text>
        </TouchableOpacity>
      )}

      <FlatList
        data={history}
        renderItem={renderHistoryItem}
        keyExtractor={(item) => item._id}
        contentContainerStyle={styles.historyList}
        showsVerticalScrollIndicator={false}
        onEndReached={handleLoadMoreHistory}
        onEndReachedThreshold={0.3}
        ListEmptyComponent={
          historyLoading ? (
            <View style={styles.historyLoading}>
              <ActivityIndicator size="small" color={COLORS.accent} />
              <Text style={styles.historyLoadingText}>Loading your journey...</Text>
            </View>
          ) : (
            <View style={styles.historyEmpty}>
              <Ionicons name="book-outline" size={48} color={COLORS.border} />
              <Text style={styles.historyEmptyTitle}>Your Journey Awaits</Text>
              <Text style={styles.historyEmptyText}>
                Your reflections, questions, and meditations will appear here
              </Text>
            </View>
          )
        }
        ListFooterComponent={
          historyLoading && history.length > 0 ? (
            <ActivityIndicator style={{ padding: SPACING.lg }} color={COLORS.accent} />
          ) : null
        }
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={COLORS.accent}
          />
        }
      />
    </View>
  );

  const renderHistoryDetailModal = () => (
    <Modal
      visible={!!selectedHistoryItem}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setSelectedHistoryItem(null)}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>
            {selectedHistoryItem?.type === 'prompt' && 'Past Reflection'}
            {selectedHistoryItem?.type === 'contemplate' && 'Past Question'}
            {selectedHistoryItem?.type === 'meditation' && 'Past Meditation'}
          </Text>
          <TouchableOpacity
            style={styles.modalCloseButton}
            onPress={() => setSelectedHistoryItem(null)}
          >
            <Ionicons name="close" size={24} color={COLORS.primary} />
          </TouchableOpacity>
        </View>

        <ScrollView
          style={styles.modalScroll}
          contentContainerStyle={styles.modalContent}
          showsVerticalScrollIndicator={false}
        >
          {selectedHistoryItem && (
            <>
              {selectedHistoryItem.type === 'prompt' && (
                <Text style={styles.historyDetailText}>
                  {selectedHistoryItem.response?.prompt}
                </Text>
              )}
              {selectedHistoryItem.type === 'contemplate' && (
                <>
                  <Text style={styles.historyDetailText}>
                    {selectedHistoryItem.response?.question}
                  </Text>
                  {selectedHistoryItem.response?.follow_up_prompts?.length > 0 && (
                    <View style={styles.historyFollowUps}>
                      <Text style={styles.followUpsLabel}>To go deeper:</Text>
                      {selectedHistoryItem.response.follow_up_prompts.map((fu, i) => (
                        <Text key={i} style={styles.followUpText}>{fu}</Text>
                      ))}
                    </View>
                  )}
                </>
              )}
              {selectedHistoryItem.type === 'meditation' && (
                <>
                  <Text style={styles.historyDetailLabel}>Opening</Text>
                  <Text style={styles.historyDetailText}>
                    {selectedHistoryItem.response?.opening}
                  </Text>
                  <Text style={styles.historyDetailLabel}>Settling</Text>
                  <Text style={styles.historyDetailText}>
                    {selectedHistoryItem.response?.settling}
                  </Text>
                  <Text style={styles.historyDetailLabel}>Closing</Text>
                  <Text style={styles.historyDetailText}>
                    {selectedHistoryItem.response?.closing}
                  </Text>
                </>
              )}

              <View style={styles.historyDetailMeta}>
                <Text style={styles.historyDetailTime}>
                  {new Date(selectedHistoryItem.created_at).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </Text>
              </View>
            </>
          )}
        </ScrollView>

        <View style={styles.modalFooter}>
          <TouchableOpacity
            style={styles.deleteHistoryButton}
            onPress={() => {
              handleDeleteHistoryItem(selectedHistoryItem);
              setSelectedHistoryItem(null);
            }}
          >
            <Ionicons name="trash-outline" size={18} color={COLORS.error} />
            <Text style={styles.deleteHistoryText}>Delete</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );

  // ============ MAIN RENDER ============

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color={COLORS.primary} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>Companion</Text>
          <Text style={styles.headerSubtitle}>Your reflection guide</Text>
        </View>
        <View style={styles.headerRight} />
      </View>

      {/* Tab Bar */}
      {renderTabBar()}

      {/* Content */}
      {activeTab === 'history' ? (
        renderHistoryTab()
      ) : (
        <>
          <ScrollView
            style={styles.scrollView}
            contentContainerStyle={styles.scrollContent}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={onRefresh}
                tintColor={COLORS.accent}
              />
            }
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            {activeTab === 'prompt' && renderPromptOptions()}
            {activeTab === 'question' && renderQuestionOptions()}
            {activeTab === 'meditation' && renderMeditationOptions()}

            <View style={styles.divider} />

            {renderContent()}
          </ScrollView>

          {/* Generate Button */}
          <View style={styles.bottomBar}>
            <TouchableOpacity
              style={[styles.generateButton, generating && styles.generateButtonDisabled]}
              onPress={handleGenerate}
              disabled={generating}
              activeOpacity={0.8}
            >
              {generating ? (
                <ActivityIndicator size="small" color={COLORS.white} />
              ) : (
                <>
                  <Ionicons
                    name={
                      activeTab === 'prompt'
                        ? 'sparkles'
                        : activeTab === 'question'
                        ? 'help-circle'
                        : 'leaf'
                    }
                    size={20}
                    color={COLORS.white}
                  />
                  <Text style={styles.generateButtonText}>
                    {currentContent ? 'Receive Another' : 'Receive Guidance'}
                  </Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        </>
      )}

      {/* Modals */}
      {renderMeditationModal()}
      {renderHistoryDetailModal()}
    </KeyboardAvoidingView>
  );
}

// Helper function
function getTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: Platform.OS === 'ios' ? 60 : 40,
    paddingHorizontal: SPACING.lg,
    paddingBottom: SPACING.md,
    backgroundColor: COLORS.card,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
  },
  headerTitle: {
    ...TYPOGRAPHY.heading,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    color: COLORS.primary,
  },
  headerSubtitle: {
    ...TYPOGRAPHY.caption,
    fontStyle: 'italic',
    marginTop: 2,
  },
  headerRight: {
    width: 40,
  },

  // Tab Bar
  tabBar: {
    flexDirection: 'row',
    backgroundColor: COLORS.card,
    paddingHorizontal: SPACING.sm,
    paddingBottom: SPACING.sm,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: SPACING.sm,
    borderRadius: 16,
    marginHorizontal: 2,
    gap: 4,
  },
  activeTab: {
    backgroundColor: 'rgba(141, 110, 99, 0.12)',
  },
  tabText: {
    fontSize: 12,
    color: COLORS.textLight,
    fontWeight: '500',
  },
  activeTabText: {
    color: COLORS.primary,
    fontWeight: '600',
  },

  // Scroll
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: SPACING.lg,
    paddingBottom: 140,
  },

  // Section Intro
  sectionIntro: {
    ...TYPOGRAPHY.body,
    color: COLORS.secondary,
    fontStyle: 'italic',
    textAlign: 'center',
    marginBottom: SPACING.lg,
    lineHeight: 24,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
  },

  // Options
  optionsContainer: {
    marginBottom: SPACING.md,
  },
  optionLabel: {
    ...TYPOGRAPHY.caption,
    color: COLORS.secondary,
    marginBottom: SPACING.sm,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  optionHint: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    fontStyle: 'italic',
    marginTop: SPACING.sm,
    textAlign: 'center',
  },
  optionChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.md,
    borderRadius: 20,
    backgroundColor: COLORS.card,
    borderWidth: 1,
    borderColor: COLORS.border,
    gap: SPACING.xs,
  },
  chipSelected: {
    backgroundColor: COLORS.accent,
    borderColor: COLORS.accent,
  },
  chipText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.secondary,
  },
  chipTextSelected: {
    color: COLORS.white,
  },

  // Category Grid
  categoryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  categoryCard: {
    width: '48%',
    padding: SPACING.md,
    borderRadius: 12,
    backgroundColor: COLORS.card,
    borderWidth: 1,
    borderColor: COLORS.border,
    alignItems: 'center',
  },
  categoryCardSelected: {
    borderColor: COLORS.accent,
    backgroundColor: 'rgba(141, 110, 99, 0.08)',
  },
  categoryLabel: {
    ...TYPOGRAPHY.body,
    fontWeight: '600',
    color: COLORS.secondary,
    marginTop: SPACING.xs,
  },
  categoryLabelSelected: {
    color: COLORS.primary,
  },
  categoryDesc: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    fontSize: 11,
    marginTop: 2,
  },

  // Depth Selector
  depthSelector: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  depthChip: {
    flex: 1,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.md,
    borderRadius: 12,
    backgroundColor: COLORS.card,
    borderWidth: 1,
    borderColor: COLORS.border,
    alignItems: 'center',
  },
  depthChipSelected: {
    backgroundColor: COLORS.accent,
    borderColor: COLORS.accent,
  },
  depthText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.secondary,
    fontWeight: '600',
  },
  depthTextSelected: {
    color: COLORS.white,
  },
  depthDesc: {
    fontSize: 10,
    color: COLORS.textLight,
    marginTop: 2,
  },
  depthDescSelected: {
    color: 'rgba(255,255,255,0.8)',
  },

  // Meditation Types
  meditationTypes: {
    gap: SPACING.sm,
  },
  meditationCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: SPACING.md,
    borderRadius: 12,
    backgroundColor: COLORS.card,
    borderWidth: 1,
    borderColor: COLORS.border,
    gap: SPACING.md,
  },
  meditationCardSelected: {
    borderColor: COLORS.accent,
    backgroundColor: 'rgba(141, 110, 99, 0.08)',
  },
  meditationIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  meditationCardContent: {
    flex: 1,
  },
  meditationCardTitle: {
    ...TYPOGRAPHY.body,
    fontWeight: '600',
    color: COLORS.secondary,
  },
  meditationCardTitleSelected: {
    color: COLORS.primary,
  },
  meditationCardDesc: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginTop: 2,
  },

  // Duration
  durationSelector: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  durationChip: {
    flex: 1,
    paddingVertical: SPACING.md,
    borderRadius: 12,
    backgroundColor: COLORS.card,
    borderWidth: 1,
    borderColor: COLORS.border,
    alignItems: 'center',
  },
  durationChipSelected: {
    backgroundColor: COLORS.accent,
    borderColor: COLORS.accent,
  },
  durationNumber: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.secondary,
  },
  durationNumberSelected: {
    color: COLORS.white,
  },
  durationLabel: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginTop: 2,
  },
  durationLabelSelected: {
    color: 'rgba(255,255,255,0.8)',
  },

  // Intention
  intentionContainer: {
    marginTop: SPACING.lg,
  },
  intentionInput: {
    backgroundColor: COLORS.card,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    padding: SPACING.md,
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    minHeight: 80,
    textAlignVertical: 'top',
  },

  // Divider
  divider: {
    height: 1,
    backgroundColor: COLORS.border,
    marginVertical: SPACING.lg,
  },

  // Loading State
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: SPACING.xxl,
  },
  breathingOrb: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(141, 110, 99, 0.2)',
    marginBottom: SPACING.lg,
  },
  loadingText: {
    ...TYPOGRAPHY.body,
    color: COLORS.secondary,
    fontStyle: 'italic',
    textAlign: 'center',
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
  },
  loadingHint: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginTop: SPACING.sm,
    fontStyle: 'italic',
  },

  // Error State
  errorContainer: {
    alignItems: 'center',
    paddingVertical: SPACING.xxl,
  },
  errorIconWrap: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: COLORS.card,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  errorTitle: {
    ...TYPOGRAPHY.heading,
    color: COLORS.secondary,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
  },
  errorText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textLight,
    marginTop: SPACING.sm,
    textAlign: 'center',
    paddingHorizontal: SPACING.lg,
    lineHeight: 24,
  },
  retryButton: {
    marginTop: SPACING.lg,
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.lg,
    borderRadius: 20,
    backgroundColor: COLORS.card,
    borderWidth: 1,
    borderColor: COLORS.accent,
    gap: SPACING.xs,
  },
  retryButtonText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.accent,
    fontWeight: '600',
  },

  // Empty State
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: SPACING.xxl,
  },
  emptyIconWrap: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(141, 110, 99, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  emptyTitle: {
    ...TYPOGRAPHY.heading,
    color: COLORS.secondary,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    textAlign: 'center',
  },
  emptySubtitle: {
    ...TYPOGRAPHY.body,
    color: COLORS.textLight,
    marginTop: SPACING.sm,
    textAlign: 'center',
    fontStyle: 'italic',
    paddingHorizontal: SPACING.lg,
    lineHeight: 24,
  },

  // Content Card
  contentCard: {
    backgroundColor: COLORS.card,
    borderRadius: 20,
    padding: SPACING.xl,
    ...SHADOWS.medium,
    alignItems: 'center',
  },
  contentIconWrap: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(141, 110, 99, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  contentLabel: {
    ...TYPOGRAPHY.caption,
    color: COLORS.accent,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: SPACING.md,
  },
  promptText: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    lineHeight: 30,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    fontSize: 18,
    textAlign: 'center',
  },
  questionText: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    lineHeight: 30,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    fontSize: 18,
    textAlign: 'center',
  },
  contentMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: SPACING.md,
    gap: SPACING.xs,
  },
  metaText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    fontStyle: 'italic',
  },
  contentInvitation: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    fontStyle: 'italic',
    marginTop: SPACING.lg,
    textAlign: 'center',
  },

  // Follow-ups
  followUps: {
    marginTop: SPACING.lg,
    paddingTop: SPACING.lg,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    width: '100%',
  },
  followUpsLabel: {
    ...TYPOGRAPHY.caption,
    color: COLORS.accent,
    fontWeight: '600',
    marginBottom: SPACING.md,
    textAlign: 'center',
  },
  followUpItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: SPACING.sm,
    paddingHorizontal: SPACING.sm,
  },
  followUpDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: COLORS.accent,
    marginTop: 8,
    marginRight: SPACING.sm,
  },
  followUpText: {
    ...TYPOGRAPHY.body,
    color: COLORS.secondary,
    flex: 1,
    lineHeight: 24,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
  },

  // Meditation Preview
  meditationPreview: {
    width: '100%',
    padding: SPACING.md,
    backgroundColor: 'rgba(141, 110, 99, 0.05)',
    borderRadius: 12,
    marginBottom: SPACING.md,
  },
  meditationPreviewTitle: {
    ...TYPOGRAPHY.caption,
    color: COLORS.accent,
    fontWeight: '600',
    marginBottom: SPACING.xs,
  },
  meditationPreviewText: {
    ...TYPOGRAPHY.body,
    color: COLORS.secondary,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    lineHeight: 24,
  },
  viewFullButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.lg,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: COLORS.accent,
    gap: SPACING.sm,
  },
  viewFullButtonText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.accent,
    fontWeight: '600',
  },

  // Bottom Bar
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: COLORS.background,
    paddingHorizontal: SPACING.lg,
    paddingTop: SPACING.md,
    paddingBottom: Platform.OS === 'ios' ? 34 : SPACING.lg,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  generateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.accent,
    paddingVertical: SPACING.md,
    borderRadius: 25,
    gap: SPACING.sm,
    ...SHADOWS.small,
  },
  generateButtonDisabled: {
    opacity: 0.7,
  },
  generateButtonText: {
    ...TYPOGRAPHY.body,
    color: COLORS.white,
    fontWeight: '600',
  },

  // Modal
  modalContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: Platform.OS === 'ios' ? 60 : 20,
    paddingHorizontal: SPACING.lg,
    paddingBottom: SPACING.md,
    backgroundColor: COLORS.card,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  modalTitle: {
    ...TYPOGRAPHY.heading,
    color: COLORS.primary,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
  },
  modalCloseButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalScroll: {
    flex: 1,
  },
  modalContent: {
    padding: SPACING.lg,
    paddingBottom: SPACING.xxl,
  },
  modalFooter: {
    padding: SPACING.lg,
    paddingBottom: Platform.OS === 'ios' ? 34 : SPACING.lg,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    backgroundColor: COLORS.card,
  },

  // Meditation Full View
  meditationFullSection: {
    marginBottom: SPACING.xl,
  },
  sectionIconRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.md,
    gap: SPACING.sm,
  },
  sectionIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  meditationSectionTitle: {
    ...TYPOGRAPHY.heading,
    fontSize: 16,
    color: COLORS.primary,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
  },
  meditationFullText: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    lineHeight: 28,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
  },
  intervalBlock: {
    marginBottom: SPACING.md,
  },
  intervalDivider: {
    alignItems: 'center',
    paddingVertical: SPACING.md,
  },
  meditationClosing: {
    alignItems: 'center',
    paddingTop: SPACING.xl,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    marginTop: SPACING.lg,
  },
  meditationClosingText: {
    ...TYPOGRAPHY.body,
    color: COLORS.secondary,
    fontStyle: 'italic',
    marginTop: SPACING.sm,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
  },

  // History
  historyContainer: {
    flex: 1,
  },
  clearAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.sm,
    gap: SPACING.xs,
  },
  clearAllText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.error,
  },
  historyList: {
    padding: SPACING.lg,
    paddingTop: 0,
  },
  historyItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    padding: SPACING.md,
    borderRadius: 12,
    marginBottom: SPACING.sm,
    ...SHADOWS.small,
  },
  historyIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.md,
  },
  historyContent: {
    flex: 1,
  },
  historyType: {
    ...TYPOGRAPHY.caption,
    color: COLORS.accent,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  historyPreview: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    marginTop: 2,
    lineHeight: 20,
  },
  historyTime: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginTop: 4,
  },
  historyLoading: {
    alignItems: 'center',
    paddingVertical: SPACING.xxl,
  },
  historyLoadingText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginTop: SPACING.sm,
  },
  historyEmpty: {
    alignItems: 'center',
    paddingVertical: SPACING.xxl,
  },
  historyEmptyTitle: {
    ...TYPOGRAPHY.heading,
    color: COLORS.secondary,
    marginTop: SPACING.md,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
  },
  historyEmptyText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textLight,
    marginTop: SPACING.sm,
    textAlign: 'center',
    fontStyle: 'italic',
    paddingHorizontal: SPACING.lg,
  },

  // History Detail Modal
  historyDetailText: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    lineHeight: 28,
    fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    fontSize: 17,
  },
  historyDetailLabel: {
    ...TYPOGRAPHY.caption,
    color: COLORS.accent,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginTop: SPACING.lg,
    marginBottom: SPACING.sm,
  },
  historyFollowUps: {
    marginTop: SPACING.lg,
    paddingTop: SPACING.md,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  historyDetailMeta: {
    marginTop: SPACING.xl,
    paddingTop: SPACING.md,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    alignItems: 'center',
  },
  historyDetailTime: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    fontStyle: 'italic',
  },
  deleteHistoryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: SPACING.md,
    gap: SPACING.sm,
  },
  deleteHistoryText: {
    ...TYPOGRAPHY.body,
    color: COLORS.error,
  },
});
