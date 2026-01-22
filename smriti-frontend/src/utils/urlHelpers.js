/**
 * URL manipulation utilities.
 */

/**
 * Build URL with query parameters
 * @param {string} baseUrl - Base URL
 * @param {Object} params - Query parameters
 * @returns {string} - URL with query string
 */
export const buildUrl = (baseUrl, params = {}) => {
  if (!params || Object.keys(params).length === 0) {
    return baseUrl;
  }
  
  const queryString = Object.entries(params)
    .filter(([_, value]) => value !== null && value !== undefined)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
  
  return `${baseUrl}${queryString ? `?${queryString}` : ''}`;
};

/**
 * Parse query string from URL
 * @param {string} url - URL with query string
 * @returns {Object} - Parsed query parameters
 */
export const parseQueryString = (url) => {
  const params = {};
  const urlObj = new URL(url);
  
  urlObj.searchParams.forEach((value, key) => {
    params[key] = value;
  });
  
  return params;
};

/**
 * Validate URL format
 * @param {string} url - URL to validate
 * @returns {boolean} - True if valid URL
 */
export const isValidUrl = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Get domain from URL
 * @param {string} url - URL
 * @returns {string} - Domain name
 */
export const getDomain = (url) => {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch {
    return '';
  }
};

/**
 * Sanitize URL
 * @param {string} url - URL to sanitize
 * @returns {string} - Sanitized URL
 */
export const sanitizeUrl = (url) => {
  if (!url) return '';
  
  // Add protocol if missing
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url;
  }
  
  return url;
};
