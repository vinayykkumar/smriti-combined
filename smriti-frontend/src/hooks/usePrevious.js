/**
 * Custom hook to get previous value.
 */
import { useRef, useEffect } from 'react';

/**
 * Get previous value of a prop or state
 * @param {any} value - Current value
 * @returns {any} - Previous value
 */
export const usePrevious = (value) => {
  const ref = useRef();

  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
};
