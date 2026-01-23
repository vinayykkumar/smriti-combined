/**
 * Error constants and messages.
 */

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  UNAUTHORIZED: 'You are not authorized. Please login again.',
  NOT_FOUND: 'Resource not found.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  UNKNOWN_ERROR: 'An unknown error occurred.',
};

export const VALIDATION_ERRORS = {
  EMAIL_REQUIRED: 'Email is required',
  EMAIL_INVALID: 'Please enter a valid email address',
  USERNAME_REQUIRED: 'Username is required',
  USERNAME_INVALID: 'Username must be 3-30 characters (letters, numbers, underscore only)',
  PASSWORD_REQUIRED: 'Password is required',
  PASSWORD_TOO_SHORT: 'Password must be at least 6 characters',
  TITLE_REQUIRED: 'Title is required',
  CONTENT_REQUIRED: 'Content is required',
};

export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Logged in successfully',
  SIGNUP_SUCCESS: 'Account created successfully',
  POST_CREATED: 'Post created successfully',
  POST_UPDATED: 'Post updated successfully',
  POST_DELETED: 'Post deleted successfully',
  PROFILE_UPDATED: 'Profile updated successfully',
};

export const QUEUE_ERRORS = {
  STORAGE_READ_FAILED: 'Unable to load saved posts. Please restart the app.',
  STORAGE_WRITE_FAILED: 'Unable to save post offline. Please try again.',
  STORAGE_CORRUPTED: 'Saved posts data was corrupted and has been reset.',
  VALIDATION_FAILED: 'Post content is invalid. Please check and try again.',
  POST_NOT_FOUND: 'Post not found in saved posts.',
  INVALID_STATUS: 'Invalid post status.',
  CONCURRENT_ACCESS: 'Another operation is in progress. Please wait.',
};

export const SYNC_ERRORS = {
  SYNC_IN_PROGRESS: 'Posts are already being synced. Please wait.',
  NO_POSTS_TO_SYNC: 'No posts to sync.',
  NETWORK_UNAVAILABLE: 'No internet connection. Posts will sync when you\'re back online.',
  SYNC_CANCELLED: 'Sync was cancelled.',
  SYNC_TIMEOUT: 'Sync took too long. Will retry automatically.',
  BATCH_FAILED: 'Failed to upload posts. Will retry automatically.',
};
