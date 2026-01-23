/**
 * Queue-specific constants for offline post queue system.
 */

export const QUEUE_STATUS = {
  PENDING: 'pending',
  SYNCING: 'syncing',
  FAILED: 'failed',
};

export const MAX_RETRY_COUNT = 3;

export const VALID_CONTENT_TYPES = ['note', 'image', 'document'];

export const LOCK_TIMEOUT_MS = 5000;
