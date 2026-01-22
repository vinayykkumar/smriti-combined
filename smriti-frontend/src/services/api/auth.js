/**
 * Authentication API service.
 */
import { apiPost, apiGet } from './client';

/**
 * Sign up a new user
 * @param {Object} userData - {username, email, password, phone (optional)}
 * @returns {Promise<Object>} - {success, data, error}
 */
export const signup = async (userData) => {
  try {
    return await apiPost('/api/auth/signup', userData, { requireAuth: false });
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Signup failed'
    };
  }
};

/**
 * Login user
 * @param {Object} credentials - {username/email/phone, password}
 * @returns {Promise<Object>} - {success, data, error}
 */
export const login = async (credentials) => {
  try {
    return await apiPost('/api/auth/login', credentials, { requireAuth: false });
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Login failed'
    };
  }
};

/**
 * Get current user
 * @returns {Promise<Object>} - {success, user, error}
 */
export const getCurrentUser = async () => {
  try {
    return await apiGet('/api/auth/me');
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to get user'
    };
  }
};

/**
 * Check if username is available
 * @param {string} username - Username to check
 * @returns {Promise<Object>} - {success, available, error}
 */
export const checkUsername = async (username) => {
  try {
    return await apiGet(`/api/auth/check-username/${username}`, {}, { requireAuth: false });
  } catch (error) {
    return {
      success: false,
      available: false,
      error: error.message || 'Failed to check username'
    };
  }
};
