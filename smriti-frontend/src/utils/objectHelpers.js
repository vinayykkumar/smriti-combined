/**
 * Object manipulation utilities.
 */

/**
 * Deep clone object
 * @param {any} obj - Object to clone
 * @returns {any} - Cloned object
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (typeof obj === 'object') {
    const cloned = {};
    Object.keys(obj).forEach(key => {
      cloned[key] = deepClone(obj[key]);
    });
    return cloned;
  }
};

/**
 * Merge objects deeply
 * @param {Object} target - Target object
 * @param {...Object} sources - Source objects
 * @returns {Object} - Merged object
 */
export const deepMerge = (target, ...sources) => {
  if (!sources.length) return target;
  const source = sources.shift();
  
  if (isObject(target) && isObject(source)) {
    for (const key in source) {
      if (isObject(source[key])) {
        if (!target[key]) Object.assign(target, { [key]: {} });
        deepMerge(target[key], source[key]);
      } else {
        Object.assign(target, { [key]: source[key] });
      }
    }
  }
  
  return deepMerge(target, ...sources);
};

/**
 * Check if value is object
 * @param {any} item - Item to check
 * @returns {boolean} - True if object
 */
const isObject = (item) => {
  return item && typeof item === 'object' && !Array.isArray(item);
};

/**
 * Pick specific keys from object
 * @param {Object} obj - Object to pick from
 * @param {Array<string>} keys - Keys to pick
 * @returns {Object} - Object with picked keys
 */
export const pick = (obj, keys) => {
  return keys.reduce((result, key) => {
    if (obj.hasOwnProperty(key)) {
      result[key] = obj[key];
    }
    return result;
  }, {});
};

/**
 * Omit specific keys from object
 * @param {Object} obj - Object to omit from
 * @param {Array<string>} keys - Keys to omit
 * @returns {Object} - Object without omitted keys
 */
export const omit = (obj, keys) => {
  const result = { ...obj };
  keys.forEach(key => delete result[key]);
  return result;
};

/**
 * Check if object is empty
 * @param {Object} obj - Object to check
 * @returns {boolean} - True if empty
 */
export const isEmpty = (obj) => {
  return Object.keys(obj).length === 0;
};
