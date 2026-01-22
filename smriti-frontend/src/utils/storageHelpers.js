/**
 * Storage helper utilities.
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEY_PREFIX } from '../constants/config';

/**
 * Get storage key with prefix
 * @param {string} key - Storage key
 * @returns {string} - Prefixed storage key
 */
const getStorageKey = (key) => {
  return `${STORAGE_KEY_PREFIX}:${key}`;
};

/**
 * Store data in AsyncStorage
 * @param {string} key - Storage key
 * @param {any} value - Value to store
 * @returns {Promise<void>}
 */
export const storeData = async (key, value) => {
  try {
    const jsonValue = JSON.stringify(value);
    await AsyncStorage.setItem(getStorageKey(key), jsonValue);
  } catch (error) {
    console.error('Error storing data:', error);
    throw error;
  }
};

/**
 * Retrieve data from AsyncStorage
 * @param {string} key - Storage key
 * @returns {Promise<any>} - Stored value or null
 */
export const getData = async (key) => {
  try {
    const jsonValue = await AsyncStorage.getItem(getStorageKey(key));
    return jsonValue != null ? JSON.parse(jsonValue) : null;
  } catch (error) {
    console.error('Error retrieving data:', error);
    return null;
  }
};

/**
 * Remove data from AsyncStorage
 * @param {string} key - Storage key
 * @returns {Promise<void>}
 */
export const removeData = async (key) => {
  try {
    await AsyncStorage.removeItem(getStorageKey(key));
  } catch (error) {
    console.error('Error removing data:', error);
    throw error;
  }
};

/**
 * Clear all app data from AsyncStorage
 * @returns {Promise<void>}
 */
export const clearAllData = async () => {
  try {
    const keys = await AsyncStorage.getAllKeys();
    const appKeys = keys.filter(key => key.startsWith(STORAGE_KEY_PREFIX));
    await AsyncStorage.multiRemove(appKeys);
  } catch (error) {
    console.error('Error clearing data:', error);
    throw error;
  }
};
