/**
 * Custom hook for managing circles state and operations
 */
import { useState, useCallback } from 'react';
import * as circlesApi from '../services/api/circles';

export function useCircles() {
  const [circles, setCircles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Load all circles for the current user
   */
  const loadCircles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await circlesApi.getCircles();
      setCircles(data);
      return data;
    } catch (err) {
      setError(err.message || 'Failed to load circles');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Create a new circle
   * @param {Object} data - { name, description }
   */
  const createCircle = useCallback(async (data) => {
    setLoading(true);
    setError(null);
    try {
      const newCircle = await circlesApi.createCircle(data);
      if (newCircle) {
        setCircles(prev => [newCircle, ...prev]);
      }
      return newCircle;
    } catch (err) {
      setError(err.message || 'Failed to create circle');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Join a circle using invite code
   * @param {string} inviteCode - 8-character code
   */
  const joinCircle = useCallback(async (inviteCode) => {
    setLoading(true);
    setError(null);
    try {
      const joinedCircle = await circlesApi.joinCircle(inviteCode);
      if (joinedCircle) {
        // Add to list if not already present
        setCircles(prev => {
          const exists = prev.some(c => c._id === joinedCircle._id);
          return exists ? prev : [joinedCircle, ...prev];
        });
      }
      return joinedCircle;
    } catch (err) {
      setError(err.message || 'Failed to join circle');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Preview a circle before joining
   * @param {string} inviteCode - 8-character code
   */
  const previewCircle = useCallback(async (inviteCode) => {
    try {
      return await circlesApi.previewCircle(inviteCode);
    } catch (err) {
      setError(err.message || 'Invalid invite code');
      throw err;
    }
  }, []);

  /**
   * Refresh circles list
   */
  const refreshCircles = useCallback(async () => {
    return loadCircles();
  }, [loadCircles]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    circles,
    loading,
    error,
    loadCircles,
    createCircle,
    joinCircle,
    previewCircle,
    refreshCircles,
    clearError
  };
}

export default useCircles;
