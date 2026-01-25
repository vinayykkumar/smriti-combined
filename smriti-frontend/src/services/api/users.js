/**
 * Users API service.
 */
import { apiGet, apiPatch } from './client';

/**
 * Fetch current user's profile with stats
 * @returns {Promise<Object>} - {success, data: {user: {...}}, error}
 */
export const fetchUserProfile = async () => {
  try {
    return await apiGet('/api/users/me');
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to fetch user profile'
    };
  }
};

/**
 * Update user profile (PATCH)
 * @param {Object} profileData - Profile data to update (timezone, latitude, longitude)
 * @returns {Promise<Object>} - {success, data, error}
 */
export const updateUserProfile = async (profileData) => {
  try {
    return await apiPatch('/api/users/me', profileData);
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to update profile'
    };
  }
};

/**
 * Sync device timezone to server
 * Call this on app load when authenticated to ensure Today's Quote works correctly
 * @returns {Promise<Object>} - {success, data, error}
 */
export const syncTimezone = async () => {
  try {
    // Get device timezone (IANA format like "America/New_York")
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    if (!timezone) {
      console.warn('Could not detect device timezone');
      return { success: false, error: 'Could not detect timezone' };
    }

    return await apiPatch('/api/users/me', { timezone });
  } catch (error) {
    // Don't fail silently - log but don't crash
    console.warn('Failed to sync timezone:', error.message);
    return {
      success: false,
      error: error.message || 'Failed to sync timezone'
    };
  }
};

/**
 * Fetch a user's public profile by user ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} - {success, data: {user: {...}}, error}
 */
export const fetchUserProfileById = async (userId) => {
  try {
    return await apiGet(`/api/users/${userId}`);
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to fetch user profile'
    };
  }
};

/**
 * Fetch posts by a specific user
 * @param {string} userId - User ID
 * @param {number} skip - Pagination offset
 * @param {number} limit - Pagination limit
 * @returns {Promise<Object>} - {success, data: {posts, total, skip, limit}, error}
 */
export const fetchUserPosts = async (userId, skip = 0, limit = 20) => {
  try {
    return await apiGet(`/api/users/${userId}/posts`, { skip, limit });
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to fetch user posts'
    };
  }
};
