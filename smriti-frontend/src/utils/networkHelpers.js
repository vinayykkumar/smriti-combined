/**
 * Network and connectivity utilities.
 */

/**
 * Check if value is online/offline status
 * @param {boolean} isConnected - Connection status
 * @returns {string} - Status string
 */
export const getNetworkStatus = (isConnected) => {
  return isConnected ? 'online' : 'offline';
};

/**
 * Format network error message
 * @param {Error} error - Network error
 * @returns {string} - Formatted error message
 */
export const formatNetworkError = (error) => {
  if (!error) return 'Network error occurred';
  
  if (error.message?.includes('timeout')) {
    return 'Request timed out. Please check your connection.';
  }
  
  if (error.message?.includes('Network request failed')) {
    return 'Network request failed. Please check your internet connection.';
  }
  
  return error.message || 'Network error occurred';
};

/**
 * Check if error is network-related
 * @param {Error} error - Error to check
 * @returns {boolean} - True if network error
 */
export const isNetworkError = (error) => {
  if (!error) return false;
  
  const networkKeywords = [
    'network',
    'timeout',
    'connection',
    'fetch',
    'ECONNREFUSED',
    'ENOTFOUND',
  ];
  
  const errorMessage = error.message?.toLowerCase() || '';
  return networkKeywords.some(keyword => errorMessage.includes(keyword));
};
