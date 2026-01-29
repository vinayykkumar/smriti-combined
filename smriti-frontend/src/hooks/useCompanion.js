import { useState, useCallback } from 'react';
import * as companionApi from '../services/api/companion';

/**
 * Custom hook for managing AI Companion state
 * @returns {object} Companion state and methods
 */
export function useCompanion() {
  // Settings state
  const [settings, setSettings] = useState(null);
  const [settingsLoading, setSettingsLoading] = useState(false);

  // Generation state
  const [generating, setGenerating] = useState(false);
  const [currentContent, setCurrentContent] = useState(null);
  const [contentType, setContentType] = useState(null); // 'prompt', 'question', 'meditation'

  // History state
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [hasMoreHistory, setHasMoreHistory] = useState(false);

  // Error state
  const [error, setError] = useState(null);

  // ============ Settings Methods ============

  const loadSettings = useCallback(async () => {
    try {
      setSettingsLoading(true);
      setError(null);
      const data = await companionApi.getSettings();
      setSettings(data);
      return data;
    } catch (err) {
      setError(err.message || 'Failed to load settings');
      console.error('Error loading companion settings:', err);
      return null;
    } finally {
      setSettingsLoading(false);
    }
  }, []);

  const updateSettings = useCallback(async (newSettings) => {
    try {
      setSettingsLoading(true);
      setError(null);
      const data = await companionApi.updateSettings(newSettings);
      setSettings(data);
      return data;
    } catch (err) {
      setError(err.message || 'Failed to update settings');
      console.error('Error updating companion settings:', err);
      return null;
    } finally {
      setSettingsLoading(false);
    }
  }, []);

  // ============ Generation Methods ============

  const generatePrompt = useCallback(async (options = {}) => {
    try {
      setGenerating(true);
      setError(null);
      const data = await companionApi.generatePrompt(options);
      setCurrentContent(data);
      setContentType('prompt');
      return data;
    } catch (err) {
      setError(err.message || 'Failed to generate prompt');
      console.error('Error generating prompt:', err);
      return null;
    } finally {
      setGenerating(false);
    }
  }, []);

  const generateQuestion = useCallback(async (options = {}) => {
    try {
      setGenerating(true);
      setError(null);
      const data = await companionApi.generateQuestion(options);
      setCurrentContent(data);
      setContentType('question');
      return data;
    } catch (err) {
      setError(err.message || 'Failed to generate question');
      console.error('Error generating question:', err);
      return null;
    } finally {
      setGenerating(false);
    }
  }, []);

  const generateMeditation = useCallback(async (options = {}) => {
    try {
      setGenerating(true);
      setError(null);
      const data = await companionApi.generateMeditation(options);
      setCurrentContent(data);
      setContentType('meditation');
      return data;
    } catch (err) {
      setError(err.message || 'Failed to generate meditation');
      console.error('Error generating meditation:', err);
      return null;
    } finally {
      setGenerating(false);
    }
  }, []);

  // ============ History Methods ============

  const loadHistory = useCallback(async (page = 1, type = null) => {
    try {
      setHistoryLoading(true);
      setError(null);
      const data = await companionApi.getHistory({ page, type });
      if (page === 1) {
        setHistory(data.entries || []);
      } else {
        setHistory(prev => [...prev, ...(data.entries || [])]);
      }
      setHasMoreHistory(data.has_more || false);
      return data;
    } catch (err) {
      setError(err.message || 'Failed to load history');
      console.error('Error loading history:', err);
      return null;
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const deleteHistoryEntry = useCallback(async (entryId) => {
    try {
      setError(null);
      await companionApi.deleteHistoryEntry(entryId);
      setHistory(prev => prev.filter(entry => entry._id !== entryId));
      return true;
    } catch (err) {
      setError(err.message || 'Failed to delete entry');
      console.error('Error deleting history entry:', err);
      return false;
    }
  }, []);

  const clearHistory = useCallback(async () => {
    try {
      setError(null);
      await companionApi.deleteAllHistory();
      setHistory([]);
      return true;
    } catch (err) {
      setError(err.message || 'Failed to clear history');
      console.error('Error clearing history:', err);
      return false;
    }
  }, []);

  // ============ Utility Methods ============

  const clearContent = useCallback(() => {
    setCurrentContent(null);
    setContentType(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // Settings
    settings,
    settingsLoading,
    loadSettings,
    updateSettings,

    // Generation
    generating,
    currentContent,
    contentType,
    generatePrompt,
    generateQuestion,
    generateMeditation,

    // History
    history,
    historyLoading,
    hasMoreHistory,
    loadHistory,
    deleteHistoryEntry,
    clearHistory,

    // Utility
    error,
    clearContent,
    clearError,
  };
}
