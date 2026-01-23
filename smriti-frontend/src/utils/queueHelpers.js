/**
 * Queue helper utilities for offline post queue system.
 */
import { QUEUE_STATUS, VALID_CONTENT_TYPES, MAX_RETRY_COUNT } from '../constants/queue';
import { MAX_POST_TITLE_LENGTH, MAX_POST_CONTENT_LENGTH } from '../constants/config';

/**
 * Generate a unique queue ID
 * @returns {string} - Unique ID in format: queue_<timestamp>_<random>
 */
export const generateQueueId = () => {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `queue_${timestamp}_${random}`;
};

/**
 * Validate post data
 * @param {object} postData - Post data to validate
 * @returns {object} - { isValid: boolean, errors: string[] }
 */
export const validatePostData = (postData) => {
  const errors = [];

  if (!postData) {
    errors.push('Post data is required');
    return { isValid: false, errors };
  }

  const { title, textContent, contentType, image, document } = postData;

  // Validate contentType
  if (!contentType || !VALID_CONTENT_TYPES.includes(contentType)) {
    errors.push(`Content type must be one of: ${VALID_CONTENT_TYPES.join(', ')}`);
  }

  // Validate title for note type
  if (contentType === 'note') {
    const trimmedTitle = title?.trim();
    if (!trimmedTitle) {
      errors.push('Title is required for note type');
    } else if (trimmedTitle.length > MAX_POST_TITLE_LENGTH) {
      errors.push(`Title must not exceed ${MAX_POST_TITLE_LENGTH} characters`);
    }
  }

  // Validate textContent length
  if (textContent && textContent.length > MAX_POST_CONTENT_LENGTH) {
    errors.push(`Content must not exceed ${MAX_POST_CONTENT_LENGTH} characters`);
  }

  // Validate image for image type
  if (contentType === 'image' && !image) {
    errors.push('Image is required for image type');
  }

  // Validate document for document type
  if (contentType === 'document' && !document) {
    errors.push('Document is required for document type');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Sanitize post data (trim strings)
 * @param {object} postData - Post data to sanitize
 * @returns {object} - Sanitized post data
 */
export const sanitizePostData = (postData) => {
  if (!postData) return postData;

  return {
    ...postData,
    title: postData.title?.trim() || '',
    textContent: postData.textContent?.trim() || '',
    contentType: postData.contentType,
    image: postData.image || null,
    document: postData.document || null,
    linkUrl: postData.linkUrl?.trim() || null,
  };
};

/**
 * Create a full queued post object
 * @param {object} postData - Post data
 * @returns {object} - Complete QueuedPost object
 */
export const createQueuedPost = (postData) => {
  const sanitized = sanitizePostData(postData);
  const now = Date.now();

  return {
    queueId: generateQueueId(),
    postData: sanitized,
    metadata: {
      status: QUEUE_STATUS.PENDING,
      createdAt: now,
      retryCount: 0,
      lastAttemptAt: null,
      lastError: null,
    },
  };
};

/**
 * Check if a post is eligible for retry
 * @param {object} post - Queued post object
 * @param {number} maxRetries - Maximum retry count (defaults to MAX_RETRY_COUNT)
 * @returns {boolean} - True if post can be retried
 */
export const isRetryEligible = (post, maxRetries = MAX_RETRY_COUNT) => {
  if (!post?.metadata) return false;
  return post.metadata.retryCount < maxRetries;
};

/**
 * Sort posts by createdAt (newest first)
 * @param {Array} posts - Array of queued posts
 * @returns {Array} - Sorted array
 */
export const sortByCreatedAt = (posts) => {
  if (!Array.isArray(posts)) return [];
  return [...posts].sort((a, b) => {
    const timeA = a?.metadata?.createdAt || 0;
    const timeB = b?.metadata?.createdAt || 0;
    return timeB - timeA;
  });
};

/**
 * Check if a queued post object is valid/well-formed
 * @param {object} post - Post object to validate
 * @returns {boolean} - True if valid
 */
export const isValidQueuedPost = (post) => {
  return !!(post?.queueId && post?.postData && post?.metadata);
};
