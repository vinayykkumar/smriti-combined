import { API_BASE_URL as ENV_API_URL, APP_NAME as ENV_APP_NAME, APP_VERSION as ENV_APP_VERSION } from '@env';

// API Configuration
export const API_BASE_URL = ENV_API_URL || 'https://smriti-backend-r293.onrender.com/api';

// App Configuration
export const APP_NAME = ENV_APP_NAME || 'Smriti';
export const APP_VERSION = ENV_APP_VERSION || '1.0.0';

// Storage Keys
export const STORAGE_KEY_PREFIX = '@smriti';
export const STORAGE_KEY_USER_TOKEN = 'user_token';
export const STORAGE_KEY_USER_DATA = 'user_data';
export const STORAGE_KEY_USERS = `${STORAGE_KEY_PREFIX}:users`;
export const STORAGE_KEY_POSTS = `${STORAGE_KEY_PREFIX}:posts`;

// Pagination
export const DEFAULT_POSTS_LIMIT = 20;
export const DEFAULT_POSTS_SKIP = 0;

// Validation
export const MIN_USERNAME_LENGTH = 3;
export const MIN_PASSWORD_LENGTH = 6;
export const MAX_POST_TITLE_LENGTH = 100;
export const MAX_POST_CONTENT_LENGTH = 5000;
