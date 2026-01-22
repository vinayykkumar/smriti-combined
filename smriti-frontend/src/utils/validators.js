/**
 * Validation utilities for frontend.
 */

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} - True if valid
 */
export const isValidEmail = (email) => {
  if (!email) return false;
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
};

/**
 * Validate username format
 * @param {string} username - Username to validate
 * @returns {boolean} - True if valid
 */
export const isValidUsername = (username) => {
  if (!username) return false;
  // 3-30 chars, alphanumeric and underscore
  const pattern = /^[a-zA-Z0-9_]{3,30}$/;
  return pattern.test(username);
};

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {boolean} - True if valid
 */
export const isValidPassword = (password) => {
  if (!password) return false;
  return password.length >= 6;
};

/**
 * Sanitize string input
 * @param {string} value - String to sanitize
 * @param {number} maxLength - Optional max length
 * @returns {string} - Sanitized string
 */
export const sanitizeString = (value, maxLength = null) => {
  if (!value) return '';
  let sanitized = value.trim();
  if (maxLength && sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
  }
  return sanitized;
};
