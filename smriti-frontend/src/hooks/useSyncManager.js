import { useEffect, useRef, useState, useCallback } from 'react';
import { AppState } from 'react-native';
import { useNetwork } from './useNetwork';
import * as syncService from '../services/syncService';
import * as postQueueService from '../services/postQueueService';
import { logError, logDebug } from '../utils/errorHandler';
import { SYNC_STATUS } from '../constants/sync';

/**
 * Configuration for automatic sync behavior
 */
const SYNC_CONFIG = {
  // Wait for network to be stable before syncing (ms)
  NETWORK_STABILITY_DELAY_MS: 2000,
  // Minimum time between auto-sync attempts (ms)
  MIN_SYNC_INTERVAL_MS: 30000,
  // Delay before syncing on app launch (ms)
  LAUNCH_SYNC_DELAY_MS: 3000,
};

/**
 * useSyncManager - Manages automatic post synchronization
 *
 * Watches for network changes and app lifecycle events to automatically
 * sync queued posts when conditions are right.
 *
 * Features:
 * - Auto-sync when coming back online (with stability delay)
 * - Auto-sync on app launch if posts are queued
 * - Auto-sync when app returns to foreground
 * - Prevents concurrent syncs
 * - Provides sync state for UI
 *
 * @param {object} options - Configuration options
 * @param {boolean} options.enabled - Enable/disable automatic syncing (default: true)
 * @param {boolean} options.syncOnLaunch - Sync on initial mount (default: true)
 * @param {boolean} options.syncOnForeground - Sync when app comes to foreground (default: true)
 * @param {boolean} options.syncOnNetworkRestore - Sync when network is restored (default: true)
 *
 * @returns {object} Sync manager state and controls
 */
export function useSyncManager(options = {}) {
  const {
    enabled = true,
    syncOnLaunch = true,
    syncOnForeground = true,
    syncOnNetworkRestore = true,
  } = options;

  const { isOnline, isStatusKnown } = useNetwork();

  // Sync state
  const [syncState, setSyncState] = useState(() => syncService.getSyncState());
  const [queueCount, setQueueCount] = useState(0);
  const [lastSyncAt, setLastSyncAt] = useState(null);

  // Refs for tracking state across renders
  const wasOnlineRef = useRef(null);
  const appStateRef = useRef(AppState.currentState);
  const networkStabilityTimerRef = useRef(null);
  const launchSyncTimerRef = useRef(null);
  const hasDoneLaunchSyncRef = useRef(false);
  const isMountedRef = useRef(true);

  /**
   * Update queue count
   */
  const updateQueueCount = useCallback(async () => {
    try {
      const result = await postQueueService.getQueueStats();
      if (result.success && isMountedRef.current) {
        const pendingCount = result.stats.pending + result.stats.failed;
        setQueueCount(pendingCount);
      }
    } catch (error) {
      logError(error, 'useSyncManager.updateQueueCount');
    }
  }, []);

  /**
   * Check if enough time has passed since last sync
   */
  const canSyncNow = useCallback(() => {
    if (!lastSyncAt) return true;
    const elapsed = Date.now() - lastSyncAt;
    return elapsed >= SYNC_CONFIG.MIN_SYNC_INTERVAL_MS;
  }, [lastSyncAt]);

  /**
   * Perform sync with guards
   */
  const performSync = useCallback(async (reason) => {
    // Guard: Check if enabled
    if (!enabled) {
      return { skipped: true, reason: 'Sync disabled' };
    }

    // Guard: Check if already syncing
    if (syncService.isSyncing()) {
      return { skipped: true, reason: 'Sync already in progress' };
    }

    // Guard: Check network
    if (!isOnline) {
      return { skipped: true, reason: 'Network offline' };
    }

    // Guard: Check if too soon since last sync
    if (!canSyncNow()) {
      return { skipped: true, reason: 'Too soon since last sync' };
    }

    // Check if there are posts to sync
    const stats = await postQueueService.getQueueStats();
    if (!stats.success || stats.stats.pending === 0) {
      await updateQueueCount();
      return { skipped: true, reason: 'No pending posts' };
    }

    logDebug(`Starting sync: ${reason}`, 'SyncManager');

    try {
      const result = await syncService.syncPendingPosts();

      if (isMountedRef.current) {
        setLastSyncAt(Date.now());
        await updateQueueCount();
      }

      logDebug(`Sync complete: ${result.synced} synced, ${result.failed} failed`, 'SyncManager');

      return { skipped: false, result };
    } catch (error) {
      logError(error, 'useSyncManager.performSync');
      return { skipped: false, error };
    }
  }, [enabled, isOnline, canSyncNow, updateQueueCount]);

  /**
   * Schedule a sync after network stability delay
   */
  const scheduleNetworkSync = useCallback(() => {
    // Clear any existing timer
    if (networkStabilityTimerRef.current) {
      clearTimeout(networkStabilityTimerRef.current);
    }

    // Schedule sync after stability delay
    networkStabilityTimerRef.current = setTimeout(() => {
      networkStabilityTimerRef.current = null;
      performSync('network restored');
    }, SYNC_CONFIG.NETWORK_STABILITY_DELAY_MS);
  }, [performSync]);

  /**
   * Manual sync trigger
   */
  const triggerSync = useCallback(() => {
    return performSync('manual trigger');
  }, [performSync]);

  /**
   * Cancel any in-progress sync
   */
  const cancelSync = useCallback(() => {
    return syncService.cancelSync();
  }, []);

  /**
   * Retry failed posts
   */
  const retryFailed = useCallback(async () => {
    const result = await syncService.retryFailedPosts();
    if (result.success && result.count > 0) {
      await updateQueueCount();
      // Trigger sync to process retried posts
      return performSync('retry failed');
    }
    return result;
  }, [performSync, updateQueueCount]);

  // Subscribe to sync progress
  useEffect(() => {
    const unsubscribe = syncService.subscribeToProgress((state) => {
      if (isMountedRef.current) {
        setSyncState(state);
      }
    });

    return unsubscribe;
  }, []);

  // Initial queue count
  useEffect(() => {
    updateQueueCount();
  }, [updateQueueCount]);

  // Handle network changes
  useEffect(() => {
    if (!syncOnNetworkRestore || !isStatusKnown) {
      return;
    }

    const wasOnline = wasOnlineRef.current;
    wasOnlineRef.current = isOnline;

    // Detect transition from offline to online
    if (wasOnline === false && isOnline === true) {
      logDebug('Network restored, scheduling sync', 'SyncManager');
      scheduleNetworkSync();
    }

    // Cleanup timer if going offline
    if (!isOnline && networkStabilityTimerRef.current) {
      clearTimeout(networkStabilityTimerRef.current);
      networkStabilityTimerRef.current = null;
    }
  }, [isOnline, isStatusKnown, syncOnNetworkRestore, scheduleNetworkSync]);

  // Handle app state changes
  useEffect(() => {
    if (!syncOnForeground) {
      return;
    }

    const handleAppStateChange = (nextAppState) => {
      const previousState = appStateRef.current;
      appStateRef.current = nextAppState;

      // Detect transition from background to foreground
      if (
        previousState.match(/inactive|background/) &&
        nextAppState === 'active'
      ) {
        logDebug('App came to foreground, checking for sync', 'SyncManager');
        performSync('app foreground');
      }
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);

    return () => {
      subscription?.remove();
    };
  }, [syncOnForeground, performSync]);

  // Handle launch sync
  useEffect(() => {
    if (!syncOnLaunch || hasDoneLaunchSyncRef.current) {
      return;
    }

    hasDoneLaunchSyncRef.current = true;

    // Delay launch sync to let app initialize
    launchSyncTimerRef.current = setTimeout(() => {
      launchSyncTimerRef.current = null;
      logDebug('Launch sync check', 'SyncManager');
      performSync('app launch');
    }, SYNC_CONFIG.LAUNCH_SYNC_DELAY_MS);

    return () => {
      if (launchSyncTimerRef.current) {
        clearTimeout(launchSyncTimerRef.current);
      }
    };
  }, [syncOnLaunch, performSync]);

  // Cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true;

    return () => {
      isMountedRef.current = false;

      if (networkStabilityTimerRef.current) {
        clearTimeout(networkStabilityTimerRef.current);
      }
      if (launchSyncTimerRef.current) {
        clearTimeout(launchSyncTimerRef.current);
      }
    };
  }, []);

  // Derived state
  const isSyncing = syncState.status === SYNC_STATUS.SYNCING;
  const hasPendingPosts = queueCount > 0;

  return {
    // State
    syncState,
    isSyncing,
    queueCount,
    hasPendingPosts,
    lastSyncAt,

    // Progress details
    progress: syncState.progress,
    currentBatch: syncState.currentBatch,
    totalBatches: syncState.totalBatches,

    // Controls
    triggerSync,
    cancelSync,
    retryFailed,
    refreshQueueCount: updateQueueCount,
  };
}

export default useSyncManager;
