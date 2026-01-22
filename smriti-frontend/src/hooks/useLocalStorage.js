/**
 * Custom hook for localStorage-like functionality with AsyncStorage.
 */
import { useState, useEffect, useCallback } from 'react';
import { getData, storeData, removeData } from '../utils/storageHelpers';

/**
 * Use local storage hook
 * @param {string} key - Storage key
 * @param {any} initialValue - Initial value
 * @returns {[any, Function, Function]} - [value, setValue, removeValue]
 */
export const useLocalStorage = (key, initialValue = null) => {
  const [storedValue, setStoredValue] = useState(initialValue);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadValue = async () => {
      try {
        const value = await getData(key);
        setStoredValue(value !== null ? value : initialValue);
      } catch (error) {
        console.error('Error loading from storage:', error);
        setStoredValue(initialValue);
      } finally {
        setLoading(false);
      }
    };

    loadValue();
  }, [key, initialValue]);

  const setValue = useCallback(async (value) => {
    try {
      setStoredValue(value);
      await storeData(key, value);
    } catch (error) {
      console.error('Error saving to storage:', error);
    }
  }, [key]);

  const removeValue = useCallback(async () => {
    try {
      setStoredValue(initialValue);
      await removeData(key);
    } catch (error) {
      console.error('Error removing from storage:', error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue, loading];
};
