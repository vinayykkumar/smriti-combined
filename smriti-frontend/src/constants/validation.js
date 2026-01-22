/**
 * Validation constants and rules.
 */

export const VALIDATION_RULES = {
  USERNAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 30,
    PATTERN: /^[a-zA-Z0-9_]+$/,
    MESSAGE: 'Username must be 3-30 characters (letters, numbers, underscore only)',
  },
  PASSWORD: {
    MIN_LENGTH: 6,
    MESSAGE: 'Password must be at least 6 characters',
  },
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    MESSAGE: 'Please enter a valid email address',
  },
  POST_TITLE: {
    MAX_LENGTH: 100,
    MESSAGE: 'Title must be 100 characters or less',
  },
  POST_CONTENT: {
    MAX_LENGTH: 5000,
    MESSAGE: 'Content must be 5000 characters or less',
  },
};

export const VALIDATION_MESSAGES = {
  REQUIRED: 'This field is required',
  INVALID_EMAIL: 'Please enter a valid email address',
  INVALID_USERNAME: 'Username must be 3-30 characters (letters, numbers, underscore only)',
  PASSWORD_TOO_SHORT: 'Password must be at least 6 characters',
  PASSWORDS_DONT_MATCH: 'Passwords do not match',
  TITLE_TOO_LONG: 'Title must be 100 characters or less',
  CONTENT_TOO_LONG: 'Content must be 5000 characters or less',
};
