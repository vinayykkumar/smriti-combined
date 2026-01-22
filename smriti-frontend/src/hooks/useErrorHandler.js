/**
 * Custom hook for error handling.
 */
import { useState, useCallback } from 'react';
import { getErrorMessage, handleApiError } from '../utils/errorHandler';

export const useErrorHandler = () => {
  const [error, setError] = useState(null);
  const [isError, setIsError] = useState(false);

  const handleError = useCallback((err) => {
    const errorInfo = handleApiError(err);
    setError(errorInfo);
    setIsError(true);
    return errorInfo;
  }, []);

  const clearError = useCallback(() => {
    setError(null);
    setIsError(false);
  }, []);

  const getErrorMessage = useCallback(() => {
    if (!error) return null;
    return error.message;
  }, [error]);

  return {
    error,
    isError,
    handleError,
    clearError,
    getErrorMessage,
  };
};
