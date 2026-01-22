/**
 * API helper utilities.
 */

/**
 * Build query string from object
 * @param {object} params - Query parameters
 * @returns {string} - Query string
 */
export const buildQueryString = (params) => {
  if (!params || Object.keys(params).length === 0) return '';
  
  const queryParams = Object.entries(params)
    .filter(([_, value]) => value !== null && value !== undefined)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
  
  return queryParams ? `?${queryParams}` : '';
};

/**
 * Get headers for API request
 * @param {string} token - Auth token
 * @param {object} additionalHeaders - Additional headers
 * @returns {object} - Headers object
 */
export const getApiHeaders = (token = null, additionalHeaders = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...additionalHeaders,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

/**
 * Handle API response
 * @param {Response} response - Fetch response
 * @returns {Promise<object>} - Parsed response data
 */
export const handleApiResponse = async (response) => {
  const data = await response.json();
  
  if (!response.ok) {
    throw {
      response,
      data,
      status: response.status,
      message: data.error || data.message || 'Request failed',
    };
  }
  
  return data;
};
