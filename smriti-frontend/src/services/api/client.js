/**
 * Base API client with shared utilities.
 */
import { API_BASE_URL } from '../../constants/config';
import { getApiHeaders, handleApiResponse, buildQueryString } from '../../utils/apiHelpers';
import { handleApiError, getErrorMessage } from '../../utils/errorHandler';
import { getData } from '../../utils/storageHelpers';
import { STORAGE_KEY_USER_TOKEN } from '../../constants/config';

/**
 * Get the auth token from storage
 * @returns {Promise<string|null>} - Auth token or null
 */
export const getAuthToken = async () => {
  try {
    const token = await getData(STORAGE_KEY_USER_TOKEN);
    return token;
  } catch (error) {
    console.error('Error getting auth token:', error);
    return null;
  }
};

/**
 * Make authenticated API request
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise<any>} - Response data
 */
export const apiRequest = async (endpoint, options = {}) => {
  try {
    const token = await getAuthToken();
    
    if (!token && options.requireAuth !== false) {
      return {
        success: false,
        error: 'No authentication token found'
      };
    }

    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    const headers = getApiHeaders(token, options.headers || {});
    
    // Remove Content-Type for FormData - React Native sets it automatically
    if (options.body instanceof FormData) {
      delete headers['Content-Type'];
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorInfo = handleApiError({ response, data: errorData });
      throw {
        response,
        data: errorData,
        ...errorInfo
      };
    }

    return await handleApiResponse(response);
  } catch (error) {
    const errorInfo = handleApiError(error);
    throw {
      ...error,
      message: getErrorMessage(errorInfo),
      ...errorInfo
    };
  }
};

/**
 * GET request helper
 * @param {string} endpoint - API endpoint
 * @param {Object} params - Query parameters
 * @param {Object} options - Additional options
 * @returns {Promise<any>} - Response data
 */
export const apiGet = async (endpoint, params = {}, options = {}) => {
  const queryString = buildQueryString(params);
  const url = queryString ? `${endpoint}${queryString}` : endpoint;
  return apiRequest(url, { ...options, method: 'GET' });
};

/**
 * POST request helper
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body
 * @param {Object} options - Additional options
 * @returns {Promise<any>} - Response data
 */
export const apiPost = async (endpoint, data, options = {}) => {
  const body = data instanceof FormData ? data : JSON.stringify(data);
  return apiRequest(endpoint, {
    ...options,
    method: 'POST',
    body,
  });
};

/**
 * PUT request helper
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body
 * @param {Object} options - Additional options
 * @returns {Promise<any>} - Response data
 */
export const apiPut = async (endpoint, data, options = {}) => {
  return apiRequest(endpoint, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(data),
  });
};

/**
 * DELETE request helper
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Additional options
 * @returns {Promise<any>} - Response data
 */
export const apiDelete = async (endpoint, options = {}) => {
  return apiRequest(endpoint, {
    ...options,
    method: 'DELETE',
  });
};
