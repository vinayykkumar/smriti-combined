/**
 * Main API service - exports all API modules.
 * 
 * This is the main entry point for API services.
 * Import from here: import { auth, posts, users } from '../services/api';
 */

// Export client utilities
export * from './client';

// Export service modules
export * as auth from './auth';
export * as posts from './posts';
export * as users from './users';
export * as notifications from './notifications';
export * as quotes from './quotes';

// Default export for backward compatibility
import * as authService from './auth';
import * as postsService from './posts';
import * as usersService from './users';
import * as notificationsService from './notifications';
import * as quotesService from './quotes';
import { getAuthToken } from './client';

export default {
  // Auth
  getAuthToken,
  signup: authService.signup,
  login: authService.login,
  getCurrentUser: authService.getCurrentUser,
  checkUsername: authService.checkUsername,

  // Posts
  fetchPosts: postsService.fetchPosts,
  createPost: postsService.createPost,
  fetchMyPosts: postsService.fetchMyPosts,
  deletePost: postsService.deletePost,

  // Users
  fetchUserProfile: usersService.fetchUserProfile,
  updateUserProfile: usersService.updateUserProfile,

  // Notifications
  registerNotificationToken: notificationsService.registerNotificationToken,
  unregisterNotificationToken: notificationsService.unregisterNotificationToken,

  // Quotes
  fetchTodayQuote: quotesService.fetchTodayQuote,
  fetchQuoteHistory: quotesService.fetchQuoteHistory,
  updateUserLocation: quotesService.updateUserLocation,
};
