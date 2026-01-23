/**
 * Sync Service - Synchronizes offline posts with the backend.
 *
 * This service orchestrates the synchronization of queued posts when
 * the device comes back online. It provides:
 *
 * FEATURES:
 * - Batch processing: Posts are synced in batches (default 10) to avoid
 *   overwhelming the server and to provide granular progress updates.
 * - Progress tracking: Subscribers receive real-time updates on sync progress.
 * - Error classification: Errors are classified as transient (retryable) or
 *   permanent (not retryable) to optimize retry behavior.
 * - Exponential backoff: Failed retries use increasing delays (1s, 2s, 4s...)
 * - Cancellation support: Long-running syncs can be cancelled gracefully.
 *
 * SYNC FLOW:
 * 1. Check network availability and concurrent sync status
 * 2. Get eligible posts (PENDING status, note/link content types)
 * 3. Mark all eligible posts as SYNCING
 * 4. Process posts in batches, sending to batch API endpoint
 * 5. For each batch result:
 *    - Success: Remove post from queue
 *    - Transient error: Increment retry count, keep as PENDING
 *    - Permanent error: Mark as FAILED
 * 6. Update progress after each batch
 * 7. On completion, set status to COMPLETED
 *
 * ERROR HANDLING:
 * - Network drops during sync: Revert remaining posts to PENDING
 * - API batch failure: Classify error and handle appropriately
 * - Unexpected errors: Log and revert posts to PENDING with error message
 */
import { apiPost } from './api/client';
import * as postQueueService from './postQueueService';
import * as networkService from './networkService';
import { logError } from '../utils/errorHandler';
import { QUEUE_STATUS, MAX_RETRY_COUNT } from '../constants/queue';
import { SYNC_ERRORS } from '../constants/errors';
import {
  SYNC_STATUS,
  SYNC_BATCH_SIZE,
  RETRY_CONFIG,
  TRANSIENT_ERROR_PATTERNS,
  PERMANENT_ERROR_PATTERNS,
  SYNC_TIMEOUTS,
} from '../constants/sync';

// Internal state
let syncState = {
  status: SYNC_STATUS.IDLE,
  progress: {
    total: 0,
    synced: 0,
    failed: 0,
    pending: 0,
  },
  currentBatch: 0,
  totalBatches: 0,
  startedAt: null,
  lastError: null,
};

let syncAbortController = null;
let progressSubscribers = [];

/**
 * Notify all progress subscribers
 */
const notifyProgressSubscribers = () => {
  const state = getSyncState();
  progressSubscribers.forEach((callback) => {
    try {
      callback(state);
    } catch (error) {
      logError(error, 'SyncService.notifyProgressSubscribers');
    }
  });
};

/**
 * Update sync state and notify subscribers
 */
const updateSyncState = (updates) => {
  syncState = { ...syncState, ...updates };
  notifyProgressSubscribers();
};

/**
 * Update progress and notify subscribers
 */
const updateProgress = (updates) => {
  syncState.progress = { ...syncState.progress, ...updates };
  notifyProgressSubscribers();
};

/**
 * Get current sync state
 */
export const getSyncState = () => ({
  ...syncState,
  progress: { ...syncState.progress },
});

/**
 * Check if sync is currently in progress
 */
export const isSyncing = () => syncState.status === SYNC_STATUS.SYNCING;

/**
 * Subscribe to sync progress updates
 * @param {Function} callback - Called with sync state on updates
 * @returns {Function} - Unsubscribe function
 */
export const subscribeToProgress = (callback) => {
  if (typeof callback !== 'function') {
    throw new Error('Callback must be a function');
  }

  progressSubscribers.push(callback);

  // Immediately call with current state
  callback(getSyncState());

  return () => {
    const index = progressSubscribers.indexOf(callback);
    if (index > -1) {
      progressSubscribers.splice(index, 1);
    }
  };
};

/**
 * Classify an error as transient or permanent
 * @param {string|Error} error - Error to classify
 * @returns {'transient'|'permanent'|'unknown'}
 */
export const classifyError = (error) => {
  const errorString = (error?.message || error || '').toLowerCase();

  // Check for permanent error patterns first (more specific)
  for (const pattern of PERMANENT_ERROR_PATTERNS) {
    if (errorString.includes(pattern.toLowerCase())) {
      return 'permanent';
    }
  }

  // Check for transient error patterns
  for (const pattern of TRANSIENT_ERROR_PATTERNS) {
    if (errorString.includes(pattern.toLowerCase())) {
      return 'transient';
    }
  }

  return 'unknown';
};

/**
 * Calculate retry delay with exponential backoff
 * @param {number} retryCount - Current retry attempt (0-indexed)
 * @returns {number} - Delay in milliseconds
 */
export const calculateRetryDelay = (retryCount) => {
  const delay = RETRY_CONFIG.BASE_DELAY_MS * Math.pow(RETRY_CONFIG.BACKOFF_MULTIPLIER, retryCount);
  return Math.min(delay, RETRY_CONFIG.MAX_DELAY_MS);
};

/**
 * Sleep for a given duration
 */
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Check if sync should continue (not cancelled, network available)
 */
const shouldContinueSync = async () => {
  if (syncAbortController?.signal.aborted) {
    return false;
  }

  const networkState = networkService.getNetworkState();
  return networkState.status !== 'offline';
};

/**
 * Transform queued post to batch API format
 */
const transformPostForBatch = (queuedPost) => ({
  queueId: queuedPost.queueId,
  contentType: queuedPost.postData.contentType,
  title: queuedPost.postData.title || null,
  textContent: queuedPost.postData.textContent || null,
  linkUrl: queuedPost.postData.linkUrl || null,
});

/**
 * Send a batch of posts to the API
 * @param {Array} posts - Array of queued posts
 * @returns {Promise<object>} - Batch result from API
 */
const sendBatch = async (posts) => {
  const batchPayload = {
    posts: posts.map(transformPostForBatch),
  };

  try {
    const response = await apiPost('/api/posts/batch', batchPayload);

    if (response.success && response.data) {
      return {
        success: true,
        data: response.data,
      };
    }

    return {
      success: false,
      error: response.error || 'Batch request failed',
    };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Batch request failed',
    };
  }
};

/**
 * Process batch results and update queue accordingly.
 *
 * For each post in the batch:
 * - If the entire batch failed, classify the error:
 *   - Transient errors (network, timeout, 5xx): Keep as PENDING, increment retry
 *   - Permanent errors (validation, 4xx): Mark as FAILED
 *   - After MAX_RETRY_COUNT: Always mark as FAILED
 *
 * - If batch succeeded, check individual results:
 *   - Success: Remove post from queue
 *   - Not in results: Mark as FAILED (server didn't process it)
 *   - Individual failure: Same error classification as above
 *
 * @param {Array} posts - Original queued posts sent in this batch
 * @param {object} batchResult - Result from batch API { success, data?, error? }
 * @returns {Promise<object>} - { synced, failed, retryable } counts
 */
const processBatchResults = async (posts, batchResult) => {
  let synced = 0;
  let failed = 0;
  let retryable = 0;

  if (!batchResult.success) {
    // Entire batch failed - mark all as needing retry (if eligible)
    for (const post of posts) {
      const errorType = classifyError(batchResult.error);
      const currentRetryCount = post.metadata?.retryCount || 0;

      if (errorType === 'transient' && currentRetryCount < MAX_RETRY_COUNT) {
        await postQueueService.updatePostStatus(post.queueId, QUEUE_STATUS.PENDING, {
          retryCount: currentRetryCount + 1,
          lastError: batchResult.error,
        });
        retryable++;
      } else {
        await postQueueService.updatePostStatus(post.queueId, QUEUE_STATUS.FAILED, {
          retryCount: currentRetryCount + 1,
          lastError: batchResult.error,
        });
        failed++;
      }
    }

    return { synced, failed, retryable };
  }

  // Process individual results
  const results = batchResult.data?.results || [];
  const resultsMap = new Map(results.map((r) => [r.queueId, r]));

  for (const post of posts) {
    const result = resultsMap.get(post.queueId);

    if (!result) {
      // Post not in results - treat as failed
      await postQueueService.updatePostStatus(post.queueId, QUEUE_STATUS.FAILED, {
        lastError: 'Post not in batch response',
      });
      failed++;
      continue;
    }

    if (result.success) {
      // Success - remove from queue
      await postQueueService.removeFromQueue(post.queueId);
      synced++;
    } else {
      // Failed - check if retryable
      const errorType = classifyError(result.error);
      const currentRetryCount = post.metadata?.retryCount || 0;

      if (errorType === 'transient' && currentRetryCount < MAX_RETRY_COUNT) {
        await postQueueService.updatePostStatus(post.queueId, QUEUE_STATUS.PENDING, {
          retryCount: currentRetryCount + 1,
          lastError: result.error,
        });
        retryable++;
      } else {
        await postQueueService.updatePostStatus(post.queueId, QUEUE_STATUS.FAILED, {
          retryCount: currentRetryCount + 1,
          lastError: result.error,
        });
        failed++;
      }
    }
  }

  return { synced, failed, retryable };
};

/**
 * Get posts eligible for sync (pending status, not exceeded retry limit)
 */
const getEligiblePosts = async () => {
  const result = await postQueueService.getQueuedPostsByStatus(QUEUE_STATUS.PENDING);

  if (!result.success) {
    return [];
  }

  // Filter to only syncable content types (note, link - not image/document)
  return result.posts.filter((post) => {
    const contentType = post.postData?.contentType;
    return contentType === 'note' || contentType === 'link';
  });
};

/**
 * Main sync function - synchronizes all pending posts
 * @returns {Promise<object>} - { success, synced, failed, error }
 */
export const syncPendingPosts = async () => {
  // Check if already syncing
  if (isSyncing()) {
    return {
      success: false,
      error: SYNC_ERRORS.SYNC_IN_PROGRESS,
      ...syncState.progress,
    };
  }

  // Check network availability
  const networkState = networkService.getNetworkState();
  if (networkState.status === 'offline') {
    return {
      success: false,
      error: SYNC_ERRORS.NETWORK_UNAVAILABLE,
      synced: 0,
      failed: 0,
    };
  }

  // Get eligible posts
  const eligiblePosts = await getEligiblePosts();

  if (eligiblePosts.length === 0) {
    return {
      success: true,
      error: null,
      synced: 0,
      failed: 0,
      message: 'No posts to sync',
    };
  }

  // Initialize sync state
  syncAbortController = new AbortController();
  const totalBatches = Math.ceil(eligiblePosts.length / SYNC_BATCH_SIZE);

  updateSyncState({
    status: SYNC_STATUS.SYNCING,
    startedAt: Date.now(),
    lastError: null,
    currentBatch: 0,
    totalBatches,
  });

  updateProgress({
    total: eligiblePosts.length,
    synced: 0,
    failed: 0,
    pending: eligiblePosts.length,
  });

  // Mark all eligible posts as syncing (batch update for performance)
  // Process in chunks to avoid overwhelming storage
  const CHUNK_SIZE = 20;
  for (let i = 0; i < eligiblePosts.length; i += CHUNK_SIZE) {
    const chunk = eligiblePosts.slice(i, i + CHUNK_SIZE);
    await Promise.all(
      chunk.map((post) =>
        postQueueService.updatePostStatus(post.queueId, QUEUE_STATUS.SYNCING)
      )
    );
  }

  let totalSynced = 0;
  let totalFailed = 0;

  try {
    // Process in batches
    for (let i = 0; i < eligiblePosts.length; i += SYNC_BATCH_SIZE) {
      // Check if we should continue
      if (!(await shouldContinueSync())) {
        // Cancelled or network dropped - revert syncing posts to pending
        const remainingPosts = eligiblePosts.slice(i);
        for (const post of remainingPosts) {
          await postQueueService.updatePostStatus(post.queueId, QUEUE_STATUS.PENDING);
        }

        updateSyncState({
          status: SYNC_STATUS.CANCELLED,
          lastError: syncAbortController?.signal.aborted
            ? SYNC_ERRORS.SYNC_CANCELLED
            : SYNC_ERRORS.NETWORK_UNAVAILABLE,
        });

        return {
          success: false,
          error: syncState.lastError,
          synced: totalSynced,
          failed: totalFailed,
        };
      }

      const batchPosts = eligiblePosts.slice(i, i + SYNC_BATCH_SIZE);
      const batchNumber = Math.floor(i / SYNC_BATCH_SIZE) + 1;

      updateSyncState({ currentBatch: batchNumber });

      // Send batch
      const batchResult = await sendBatch(batchPosts);

      // Process results
      const { synced, failed, retryable } = await processBatchResults(batchPosts, batchResult);

      totalSynced += synced;
      totalFailed += failed;

      updateProgress({
        synced: totalSynced,
        failed: totalFailed,
        pending: eligiblePosts.length - (i + batchPosts.length) + retryable,
      });

      // Small delay between batches to avoid overwhelming the server
      if (i + SYNC_BATCH_SIZE < eligiblePosts.length) {
        await sleep(500);
      }
    }

    // Sync completed
    updateSyncState({
      status: SYNC_STATUS.COMPLETED,
      lastError: null,
    });

    return {
      success: true,
      error: null,
      synced: totalSynced,
      failed: totalFailed,
    };
  } catch (error) {
    logError(error, 'SyncService.syncPendingPosts');

    // Revert any syncing posts to pending
    const currentPosts = await postQueueService.getQueuedPostsByStatus(QUEUE_STATUS.SYNCING);
    if (currentPosts.success) {
      for (const post of currentPosts.posts) {
        await postQueueService.updatePostStatus(post.queueId, QUEUE_STATUS.PENDING, {
          lastError: error.message,
        });
      }
    }

    updateSyncState({
      status: SYNC_STATUS.FAILED,
      lastError: error.message || 'Sync failed',
    });

    return {
      success: false,
      error: error.message || 'Sync failed',
      synced: totalSynced,
      failed: totalFailed,
    };
  } finally {
    syncAbortController = null;
  }
};

/**
 * Cancel an in-progress sync
 */
export const cancelSync = () => {
  if (syncAbortController) {
    syncAbortController.abort();
    updateSyncState({
      status: SYNC_STATUS.CANCELLED,
      lastError: SYNC_ERRORS.SYNC_CANCELLED,
    });
    return true;
  }
  return false;
};

/**
 * Retry failed posts
 * Resets failed posts to pending status for another sync attempt
 * @returns {Promise<object>} - { success, count }
 */
export const retryFailedPosts = async () => {
  const result = await postQueueService.getQueuedPostsByStatus(QUEUE_STATUS.FAILED);

  if (!result.success) {
    return { success: false, count: 0, error: result.error };
  }

  let resetCount = 0;

  for (const post of result.posts) {
    // Only retry if under max retry count
    if ((post.metadata?.retryCount || 0) < MAX_RETRY_COUNT) {
      await postQueueService.updatePostStatus(post.queueId, QUEUE_STATUS.PENDING);
      resetCount++;
    }
  }

  return { success: true, count: resetCount };
};

/**
 * Get sync statistics
 */
export const getSyncStats = async () => {
  const queueStats = await postQueueService.getQueueStats();

  return {
    ...getSyncState(),
    queue: queueStats.success ? queueStats.stats : null,
  };
};

/**
 * Reset sync state (for testing)
 */
export const _resetForTesting = () => {
  syncState = {
    status: SYNC_STATUS.IDLE,
    progress: {
      total: 0,
      synced: 0,
      failed: 0,
      pending: 0,
    },
    currentBatch: 0,
    totalBatches: 0,
    startedAt: null,
    lastError: null,
  };
  syncAbortController = null;
  progressSubscribers = [];
};
