/**
 * Sync-related constants for offline post synchronization.
 */

// Sync status values
export const SYNC_STATUS = {
  IDLE: 'idle',
  SYNCING: 'syncing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
};

// Batch configuration
export const SYNC_BATCH_SIZE = 10; // Posts per API request
export const MAX_CONCURRENT_BATCHES = 1; // Process batches sequentially for now

// Retry configuration
export const RETRY_CONFIG = {
  MAX_RETRIES: 3,
  BASE_DELAY_MS: 1000, // 1 second
  MAX_DELAY_MS: 30000, // 30 seconds
  BACKOFF_MULTIPLIER: 2, // Exponential backoff factor
};

// Error classification
// Transient errors can be retried, permanent errors cannot
export const TRANSIENT_ERROR_PATTERNS = [
  'network',
  'timeout',
  'ECONNREFUSED',
  'ENOTFOUND',
  'ETIMEDOUT',
  'fetch failed',
  '500',
  '502',
  '503',
  '504',
  'server error',
  'temporarily unavailable',
];

export const PERMANENT_ERROR_PATTERNS = [
  'validation',
  '400',
  '401',
  '403',
  '404',
  'invalid',
  'required',
  'unauthorized',
  'forbidden',
];

// Timeouts
export const SYNC_TIMEOUTS = {
  BATCH_REQUEST_MS: 30000, // 30 seconds per batch request
  OVERALL_SYNC_MS: 300000, // 5 minutes max for entire sync
};
