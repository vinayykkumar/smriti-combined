/**
 * Error handling utilities.
 */

/**
 * Extract error message from error object
 * @param {Error|object} error - Error object
 * @returns {string} - Error message
 */
export const getErrorMessage = (error) => {
  if (!error) return 'An unknown error occurred';
  
  if (typeof error === 'string') return error;
  
  if (error.message) return error.message;
  
  if (error.error) return error.error;
  
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  return 'An error occurred';
};

/**
 * Handle API error response
 * @param {Error} error - Error object
 * @returns {object} - Formatted error object
 */
export const handleApiError = (error) => {
  const message = getErrorMessage(error);
  const status = error.response?.status || 500;
  
  return {
    message,
    status,
    isNetworkError: !error.response,
    isServerError: status >= 500,
    isClientError: status >= 400 && status < 500,
  };
};

/**
 * Log error for debugging
 * @param {Error|object} error - Error object
 * @param {string} context - Context where error occurred
 */
export const logError = (error, context = '') => {
  const message = getErrorMessage(error);
  console.error(`[${context}]`, message, error);
  
  // In production, you might want to send to error tracking service
  // e.g., Sentry, LogRocket, etc.
};

/**
 * Log debug message (only in development)
 * @param {string} message - Debug message
 * @param {string} context - Context for the log
 * @param {any} data - Optional data to log
 */
export const logDebug = (message, context = '', data = null) => {
  if (__DEV__) {
    if (data) {
      console.log(`[${context}] ${message}`, data);
    } else {
      console.log(`[${context}] ${message}`);
    }
  }
};
