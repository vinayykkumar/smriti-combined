/**
 * API service for Today's Quote feature.
 */
import { apiGet, apiPatch } from './client';

/**
 * Fetch today's quote for the current user
 * @returns {Promise<Object>} Quote response with has_quote, status, quote data
 */
export const fetchTodayQuote = async () => {
    const response = await apiGet('/api/quotes/today');
    return response;
};

/**
 * Fetch quote history for the current user
 * @param {number} skip - Number of quotes to skip (pagination)
 * @param {number} limit - Maximum quotes to return
 * @returns {Promise<Object>} History response with quotes array and pagination info
 */
export const fetchQuoteHistory = async (skip = 0, limit = 20) => {
    const response = await apiGet('/api/quotes/history', { skip, limit });
    return response;
};

/**
 * Update user's timezone and location
 * @param {Object} data - { timezone, latitude, longitude }
 * @returns {Promise<Object>} Updated user data
 */
export const updateUserLocation = async (data) => {
    const response = await apiPatch('/api/users/me', data);
    return response;
};
