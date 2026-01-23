/**
 * Post Queue Service - Core service for offline post queue management.
 * Provides CRUD operations with concurrency safety and corruption recovery.
 */
import { storeData, getData } from '../utils/storageHelpers';
import { logError } from '../utils/errorHandler';
import { STORAGE_KEY_POST_QUEUE } from '../constants/config';
import { QUEUE_ERRORS } from '../constants/errors';
import { QUEUE_STATUS, LOCK_TIMEOUT_MS } from '../constants/queue';
import {
  createQueuedPost,
  validatePostData,
  sortByCreatedAt,
  isValidQueuedPost,
} from '../utils/queueHelpers';

// Mutex lock for concurrency safety
let operationLock = false;
let lockWaiters = [];

/**
 * Acquire the operation lock
 * @param {number} timeout - Maximum time to wait for lock in ms
 * @returns {Promise<boolean>} - True if lock acquired
 */
const acquireLock = async (timeout = LOCK_TIMEOUT_MS) => {
  if (!operationLock) {
    operationLock = true;
    return true;
  }

  return new Promise((resolve) => {
    const timeoutId = setTimeout(() => {
      const index = lockWaiters.indexOf(waiter);
      if (index > -1) {
        lockWaiters.splice(index, 1);
      }
      resolve(false);
    }, timeout);

    const waiter = () => {
      clearTimeout(timeoutId);
      operationLock = true;
      resolve(true);
    };

    lockWaiters.push(waiter);
  });
};

/**
 * Release the operation lock
 */
const releaseLock = () => {
  if (lockWaiters.length > 0) {
    const nextWaiter = lockWaiters.shift();
    nextWaiter();
  } else {
    operationLock = false;
  }
};

/**
 * Execute operation with lock
 * @param {Function} operation - Async operation to execute
 * @returns {Promise<object>} - Operation result
 */
const withLock = async (operation) => {
  const acquired = await acquireLock(LOCK_TIMEOUT_MS);
  if (!acquired) {
    return { success: false, error: QUEUE_ERRORS.CONCURRENT_ACCESS };
  }

  try {
    return await operation();
  } finally {
    releaseLock();
  }
};

/**
 * Safely read queue with corruption recovery
 * @returns {Promise<Array>} - Array of valid queued posts
 */
const safeReadQueue = async () => {
  try {
    const data = await getData(STORAGE_KEY_POST_QUEUE);

    if (data === null) {
      return [];
    }

    if (!Array.isArray(data)) {
      logError(new Error(QUEUE_ERRORS.STORAGE_CORRUPTED), 'PostQueue');
      await storeData(STORAGE_KEY_POST_QUEUE, []);
      return [];
    }

    // Filter out malformed entries
    const validPosts = data.filter(isValidQueuedPost);

    if (validPosts.length !== data.length) {
      const corruptedCount = data.length - validPosts.length;
      logError(
        new Error(`Filtered ${corruptedCount} corrupted entries from queue`),
        'PostQueue'
      );
      await storeData(STORAGE_KEY_POST_QUEUE, validPosts);
    }

    return validPosts;
  } catch (error) {
    logError(error, 'PostQueue.safeReadQueue');
    return [];
  }
};

/**
 * Add a post to the queue
 * @param {object} postData - Post data to queue
 * @returns {Promise<object>} - { success: boolean, queuedPost?: object, error?: string }
 */
export const addToQueue = async (postData) => {
  return withLock(async () => {
    // Validate post data
    const validation = validatePostData(postData);
    if (!validation.isValid) {
      return {
        success: false,
        error: QUEUE_ERRORS.VALIDATION_FAILED,
        validationErrors: validation.errors,
      };
    }

    try {
      const queue = await safeReadQueue();
      const queuedPost = createQueuedPost(postData);

      // Add to front of queue (newest first)
      const updatedQueue = [queuedPost, ...queue];

      await storeData(STORAGE_KEY_POST_QUEUE, updatedQueue);

      return { success: true, queuedPost };
    } catch (error) {
      logError(error, 'PostQueue.addToQueue');
      return { success: false, error: QUEUE_ERRORS.STORAGE_WRITE_FAILED };
    }
  });
};

/**
 * Get all queued posts
 * @returns {Promise<object>} - { success: boolean, posts?: Array, error?: string }
 */
export const getQueuedPosts = async () => {
  return withLock(async () => {
    try {
      const posts = await safeReadQueue();
      return { success: true, posts: sortByCreatedAt(posts) };
    } catch (error) {
      logError(error, 'PostQueue.getQueuedPosts');
      return { success: false, error: QUEUE_ERRORS.STORAGE_READ_FAILED, posts: [] };
    }
  });
};

/**
 * Get a queued post by ID
 * @param {string} queueId - Queue ID to find
 * @returns {Promise<object>} - { success: boolean, post?: object, error?: string }
 */
export const getQueuedPostById = async (queueId) => {
  return withLock(async () => {
    try {
      const posts = await safeReadQueue();
      const post = posts.find((p) => p.queueId === queueId);

      if (!post) {
        return { success: false, error: QUEUE_ERRORS.POST_NOT_FOUND };
      }

      return { success: true, post };
    } catch (error) {
      logError(error, 'PostQueue.getQueuedPostById');
      return { success: false, error: QUEUE_ERRORS.STORAGE_READ_FAILED };
    }
  });
};

/**
 * Get queued posts by status
 * @param {string} status - Status to filter by
 * @returns {Promise<object>} - { success: boolean, posts?: Array, error?: string }
 */
export const getQueuedPostsByStatus = async (status) => {
  return withLock(async () => {
    const validStatuses = Object.values(QUEUE_STATUS);
    if (!validStatuses.includes(status)) {
      return { success: false, error: QUEUE_ERRORS.INVALID_STATUS, posts: [] };
    }

    try {
      const posts = await safeReadQueue();
      const filtered = posts.filter((p) => p.metadata?.status === status);
      return { success: true, posts: sortByCreatedAt(filtered) };
    } catch (error) {
      logError(error, 'PostQueue.getQueuedPostsByStatus');
      return { success: false, error: QUEUE_ERRORS.STORAGE_READ_FAILED, posts: [] };
    }
  });
};

/**
 * Update post status
 * @param {string} queueId - Queue ID to update
 * @param {string} status - New status
 * @param {object} options - Optional: { retryCount, lastError }
 * @returns {Promise<object>} - { success: boolean, post?: object, error?: string }
 */
export const updatePostStatus = async (queueId, status, options = {}) => {
  return withLock(async () => {
    const validStatuses = Object.values(QUEUE_STATUS);
    if (!validStatuses.includes(status)) {
      return { success: false, error: QUEUE_ERRORS.INVALID_STATUS };
    }

    try {
      const posts = await safeReadQueue();
      const index = posts.findIndex((p) => p.queueId === queueId);

      if (index === -1) {
        return { success: false, error: QUEUE_ERRORS.POST_NOT_FOUND };
      }

      const updatedPost = {
        ...posts[index],
        metadata: {
          ...posts[index].metadata,
          status,
          lastAttemptAt: Date.now(),
          ...(options.retryCount !== undefined && { retryCount: options.retryCount }),
          ...(options.lastError !== undefined && { lastError: options.lastError }),
        },
      };

      posts[index] = updatedPost;
      await storeData(STORAGE_KEY_POST_QUEUE, posts);

      return { success: true, post: updatedPost };
    } catch (error) {
      logError(error, 'PostQueue.updatePostStatus');
      return { success: false, error: QUEUE_ERRORS.STORAGE_WRITE_FAILED };
    }
  });
};

/**
 * Remove a post from the queue
 * @param {string} queueId - Queue ID to remove
 * @returns {Promise<object>} - { success: boolean, error?: string }
 */
export const removeFromQueue = async (queueId) => {
  return withLock(async () => {
    try {
      const posts = await safeReadQueue();
      const index = posts.findIndex((p) => p.queueId === queueId);

      if (index === -1) {
        return { success: false, error: QUEUE_ERRORS.POST_NOT_FOUND };
      }

      posts.splice(index, 1);
      await storeData(STORAGE_KEY_POST_QUEUE, posts);

      return { success: true };
    } catch (error) {
      logError(error, 'PostQueue.removeFromQueue');
      return { success: false, error: QUEUE_ERRORS.STORAGE_WRITE_FAILED };
    }
  });
};

/**
 * Get queue statistics
 * @returns {Promise<object>} - { success: boolean, stats?: { total, pending, syncing, failed }, error?: string }
 */
export const getQueueStats = async () => {
  return withLock(async () => {
    try {
      const posts = await safeReadQueue();

      const stats = {
        total: posts.length,
        pending: posts.filter((p) => p.metadata?.status === QUEUE_STATUS.PENDING).length,
        syncing: posts.filter((p) => p.metadata?.status === QUEUE_STATUS.SYNCING).length,
        failed: posts.filter((p) => p.metadata?.status === QUEUE_STATUS.FAILED).length,
      };

      return { success: true, stats };
    } catch (error) {
      logError(error, 'PostQueue.getQueueStats');
      return { success: false, error: QUEUE_ERRORS.STORAGE_READ_FAILED };
    }
  });
};

/**
 * Get queue count
 * @returns {Promise<object>} - { success: boolean, count?: number, error?: string }
 */
export const getQueueCount = async () => {
  return withLock(async () => {
    try {
      const posts = await safeReadQueue();
      return { success: true, count: posts.length };
    } catch (error) {
      logError(error, 'PostQueue.getQueueCount');
      return { success: false, error: QUEUE_ERRORS.STORAGE_READ_FAILED, count: 0 };
    }
  });
};

/**
 * Clear all posts from queue (for dev/testing)
 * @returns {Promise<object>} - { success: boolean, error?: string }
 */
export const clearQueue = async () => {
  return withLock(async () => {
    try {
      await storeData(STORAGE_KEY_POST_QUEUE, []);
      return { success: true };
    } catch (error) {
      logError(error, 'PostQueue.clearQueue');
      return { success: false, error: QUEUE_ERRORS.STORAGE_WRITE_FAILED };
    }
  });
};

/**
 * Reset lock state (for testing only)
 */
export const _resetLockForTesting = () => {
  operationLock = false;
  lockWaiters = [];
};
