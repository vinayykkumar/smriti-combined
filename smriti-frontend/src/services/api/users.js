/**
 * Users API service.
 */
import { apiGet, apiPut } from './client';

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
 * Update user profile
 * @param {Object} profileData - Profile data to update
 * @returns {Promise<Object>} - {success, data, error}
 */
export const updateUserProfile = async (profileData) => {
  try {
    return await apiPut('/api/users/me', profileData);
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to update profile'
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
