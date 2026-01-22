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
