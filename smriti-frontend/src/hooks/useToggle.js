/**
 * Custom hook for toggling boolean values.
 */
import { useState, useCallback } from 'react';

/**
 * Toggle hook
 * @param {boolean} initialValue - Initial value
 * @returns {[boolean, Function, Function, Function]} - [value, toggle, setTrue, setFalse]
 */
export const useToggle = (initialValue = false) => {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => {
    setValue(prev => !prev);
  }, []);

  const setTrue = useCallback(() => {
    setValue(true);
  }, []);

  const setFalse = useCallback(() => {
    setValue(false);
  }, []);

  return [value, toggle, setTrue, setFalse];
};
