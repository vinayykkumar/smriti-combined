/**
 * AI Companion API service
 *
 * Handles all AI companion related API calls:
 * - Settings management
 * - Reflection prompts
 * - Contemplative questions
 * - Meditation guidance
 * - Conversation history
 */

import { apiGet, apiPost, apiPut, apiDelete } from './client';

const COMPANION_BASE = '/api/ai/companion';

// ============ Settings ============

/**
 * Get user's companion settings
 * @returns {Promise<Object>} Companion settings
 */
export const getSettings = async () => {
  return await apiGet(`${COMPANION_BASE}/settings`);
};

/**
 * Update user's companion settings
 * @param {Object} settings - Settings to update
 * @returns {Promise<Object>} Updated settings
 */
export const updateSettings = async (settings) => {
  return await apiPut(`${COMPANION_BASE}/settings`, settings);
};

// ============ AI Generation ============

/**
 * Generate a personalized reflection prompt
 * @param {Object} options - Generation options
 * @param {string} [options.mood] - Current mood (calm, anxious, grateful, etc.)
 * @param {string} [options.theme] - Preferred theme
 * @param {boolean} [options.use_reflections] - Whether to use past reflections for personalization
 * @returns {Promise<Object>} Generated prompt with metadata
 */
export const generatePrompt = async (options = {}) => {
  return await apiPost(`${COMPANION_BASE}/prompt`, {
    mood: options.mood || null,
    theme: options.theme || null,
    use_reflections: options.useReflections !== false,
  });
};

/**
 * Generate a contemplative question
 * @param {Object} options - Generation options
 * @param {string} [options.category] - Question category (self, relationships, purpose, presence, gratitude)
 * @param {string} [options.depth] - Depth level (gentle, moderate, deep)
 * @param {string} [options.context] - Additional context
 * @returns {Promise<Object>} Generated question with follow-ups
 */
export const generateQuestion = async (options = {}) => {
  return await apiPost(`${COMPANION_BASE}/question`, {
    category: options.category || 'self',
    depth: options.depth || 'moderate',
    context: options.context || null,
  });
};

/**
 * Generate meditation guidance
 * @param {Object} options - Generation options
 * @param {string} [options.guidanceType] - Type (sankalpam, breath-focus, depth-focus)
 * @param {number} [options.durationMinutes] - Duration in minutes (1-60)
 * @param {string} [options.intention] - User's intention for the meditation
 * @returns {Promise<Object>} Meditation guidance with sections
 */
export const generateMeditation = async (options = {}) => {
  return await apiPost(`${COMPANION_BASE}/meditation`, {
    guidance_type: options.guidanceType || 'breath-focus',
    duration_minutes: options.durationMinutes || 10,
    intention: options.intention || null,
  });
};

/**
 * Convert text to speech audio
 * @param {Object} options - TTS options
 * @param {string} options.text - Text to convert
 * @param {string} [options.voice] - Voice (alloy, echo, fable, onyx, nova, shimmer)
 * @param {number} [options.speed] - Speed (0.25 to 4.0)
 * @returns {Promise<Blob>} Audio data
 */
export const textToSpeech = async (options) => {
  // This returns binary audio data, so we need special handling
  const response = await apiPost(`${COMPANION_BASE}/tts`, {
    text: options.text,
    voice: options.voice || 'nova',
    speed: options.speed || 1.0,
  });
  return response;
};

// ============ Conversation History ============

/**
 * Get conversation history
 * @param {Object} options - Pagination options
 * @param {number} [options.page] - Page number (default: 1)
 * @param {number} [options.limit] - Items per page (default: 20)
 * @param {string} [options.type] - Filter by type (prompt, contemplate, meditation)
 * @returns {Promise<Object>} Paginated history with entries
 */
export const getHistory = async (options = {}) => {
  const params = {
    page: options.page || 1,
    limit: options.limit || 20,
  };
  if (options.type) {
    params.type = options.type;
  }
  return await apiGet(`${COMPANION_BASE}/history`, params);
};

/**
 * Delete a specific history entry
 * @param {string} entryId - Entry ID to delete
 * @returns {Promise<Object>} Success response
 */
export const deleteHistoryEntry = async (entryId) => {
  return await apiDelete(`${COMPANION_BASE}/history/${entryId}`);
};

/**
 * Delete all conversation history
 * @returns {Promise<Object>} Success response with deleted count
 */
export const deleteAllHistory = async () => {
  return await apiDelete(`${COMPANION_BASE}/history`);
};

// ============ Analysis ============

/**
 * Analyze patterns in user's reflections
 * Requires opt-in to reflection analysis in settings
 * @returns {Promise<Object>} Analysis results with themes, tone, concerns, growth indicators
 */
export const analyzeReflections = async () => {
  return await apiPost(`${COMPANION_BASE}/analyze`, {});
};
