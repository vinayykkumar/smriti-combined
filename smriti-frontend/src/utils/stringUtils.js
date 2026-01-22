/**
 * String manipulation utilities.
 */

/**
 * Capitalize first letter
 * @param {string} str - String to capitalize
 * @returns {string} - Capitalized string
 */
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

/**
 * Capitalize each word
 * @param {string} str - String to capitalize
 * @returns {string} - String with capitalized words
 */
export const capitalizeWords = (str) => {
  if (!str) return '';
  return str.split(' ').map(word => capitalize(word)).join(' ');
};

/**
 * Convert to slug
 * @param {string} text - Text to slugify
 * @returns {string} - Slug string
 */
export const slugify = (text) => {
  if (!text) return '';
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

/**
 * Remove HTML tags
 * @param {string} html - HTML string
 * @returns {string} - Plain text
 */
export const stripHtml = (html) => {
  if (!html) return '';
  return html.replace(/<[^>]*>/g, '');
};

/**
 * Extract text between tags
 * @param {string} text - Text with tags
 * @param {string} tag - Tag name
 * @returns {Array<string>} - Array of extracted texts
 */
export const extractTagContent = (text, tag) => {
  if (!text) return [];
  const regex = new RegExp(`<${tag}[^>]*>(.*?)</${tag}>`, 'gi');
  const matches = [];
  let match;
  while ((match = regex.exec(text)) !== null) {
    matches.push(match[1]);
  }
  return matches;
};
