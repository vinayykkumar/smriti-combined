/**
 * Array manipulation utilities.
 */

/**
 * Remove duplicates from array
 * @param {Array} array - Array to deduplicate
 * @returns {Array} - Array without duplicates
 */
export const unique = (array) => {
  return [...new Set(array)];
};

/**
 * Group array by key
 * @param {Array} array - Array to group
 * @param {string|Function} key - Key to group by
 * @returns {Object} - Grouped object
 */
export const groupBy = (array, key) => {
  return array.reduce((result, item) => {
    const groupKey = typeof key === 'function' ? key(item) : item[key];
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {});
};

/**
 * Sort array by key
 * @param {Array} array - Array to sort
 * @param {string} key - Key to sort by
 * @param {boolean} ascending - Sort order
 * @returns {Array} - Sorted array
 */
export const sortBy = (array, key, ascending = true) => {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (aVal < bVal) return ascending ? -1 : 1;
    if (aVal > bVal) return ascending ? 1 : -1;
    return 0;
  });
};

/**
 * Chunk array into smaller arrays
 * @param {Array} array - Array to chunk
 * @param {number} size - Chunk size
 * @returns {Array} - Array of chunks
 */
export const chunk = (array, size) => {
  const chunks = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
};

/**
 * Flatten nested array
 * @param {Array} array - Array to flatten
 * @param {number} depth - Flattening depth
 * @returns {Array} - Flattened array
 */
export const flatten = (array, depth = 1) => {
  return array.flat(depth);
};

/**
 * Get random item from array
 * @param {Array} array - Array to pick from
 * @returns {any} - Random item
 */
export const randomItem = (array) => {
  return array[Math.floor(Math.random() * array.length)];
};

/**
 * Shuffle array
 * @param {Array} array - Array to shuffle
 * @returns {Array} - Shuffled array
 */
export const shuffle = (array) => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};
