/**
 * Device and platform utilities.
 */
import { Platform } from 'react-native';

/**
 * Check if running on iOS
 * @returns {boolean} - True if iOS
 */
export const isIOS = () => {
  return Platform.OS === 'ios';
};

/**
 * Check if running on Android
 * @returns {boolean} - True if Android
 */
export const isAndroid = () => {
  return Platform.OS === 'android';
};

/**
 * Get platform name
 * @returns {string} - Platform name ('ios' or 'android')
 */
export const getPlatform = () => {
  return Platform.OS;
};

/**
 * Get platform version
 * @returns {string|number} - Platform version
 */
export const getPlatformVersion = () => {
  return Platform.Version;
};

/**
 * Check if device is tablet
 * @returns {boolean} - True if tablet
 */
export const isTablet = () => {
  // Simple check - can be enhanced with actual device detection
  const { width, height } = require('react-native').Dimensions.get('window');
  const aspectRatio = height / width;
  return aspectRatio < 1.6 && Math.max(width, height) >= 768;
};
