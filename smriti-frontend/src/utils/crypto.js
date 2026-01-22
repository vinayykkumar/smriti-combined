import CryptoJS from 'crypto-js';

/**
 * Hash a password using SHA256
 * @param {string} password - Plain text password
 * @returns {string} - Hashed password
 */
export const hashPassword = (password) => {
    return CryptoJS.SHA256(password).toString();
};

/**
 * Verify a password against a hash
 * @param {string} password - Plain text password
 * @param {string} hash - Hashed password to compare
 * @returns {boolean} - True if password matches
 */
export const verifyPassword = (password, hash) => {
    return hashPassword(password) === hash;
};

/**
 * Generate a simple UUID
 * @returns {string} - UUID string
 */
export const generateId = () => {
    return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};
