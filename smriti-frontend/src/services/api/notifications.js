/**
 * Notifications API service.
 */
import { apiPost } from './client';

/**
 * Register device token for push notifications
 * @param {string} token - FCM device token
 * @param {string} platform - 'ios' or 'android'
 * @returns {Promise<Object>} - {success, message, error}
 */
export const registerNotificationToken = async (token, platform) => {
  try {
    return await apiPost('/api/notifications/register-token', {
      token,
      platform
    });
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to register notification token'
    };
  }
};

/**
 * Unregister device token from push notifications
 * @param {string} token - FCM device token
 * @param {string} platform - 'ios' or 'android'
 * @returns {Promise<Object>} - {success, message, error}
 */
export const unregisterNotificationToken = async (token, platform) => {
  try {
    return await apiPost('/api/notifications/unregister-token', {
      token,
      platform
    });
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to unregister notification token'
    };
  }
};
