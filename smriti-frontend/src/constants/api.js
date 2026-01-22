/**
 * API endpoint constants.
 */
import { API_BASE_URL } from './config';

export const API_ENDPOINTS = {
  // Health
  HEALTH: '/health',
  HEALTH_DB: '/health/db',
  
  // Authentication
  AUTH_SIGNUP: '/api/auth/signup',
  AUTH_LOGIN: '/api/auth/login',
  AUTH_ME: '/api/auth/me',
  AUTH_CHECK_USERNAME: '/api/auth/check-username',
  
  // Posts
  POSTS: '/api/posts',
  POST_BY_ID: (id) => `/api/posts/${id}`,
  
  // Users
  USER_ME: '/api/users/me',
  USER_PROFILE: (userId) => `/api/users/${userId}`,
  
  // Notifications
  NOTIFICATIONS: '/api/notifications',
};

/**
 * Get full API URL for endpoint
 * @param {string} endpoint - API endpoint
 * @returns {string} - Full URL
 */
export const getApiUrl = (endpoint) => {
  return `${API_BASE_URL}${endpoint}`;
};
