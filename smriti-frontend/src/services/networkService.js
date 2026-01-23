/**
 * Network Service - Core network monitoring with actual internet verification.
 *
 * Provides reliable network state detection that distinguishes between:
 * - Being connected to a network (WiFi/cellular)
 * - Actually having internet access (can reach servers)
 *
 * Handles edge cases like captive portals, ISP outages, and rapid network changes.
 */
import NetInfo from '@react-native-community/netinfo';
import { API_BASE_URL } from '../constants/config';
import { logError } from '../utils/errorHandler';
import {
  NETWORK_STATUS,
  CONNECTION_TYPE,
  NETWORK_TIMEOUTS,
  NETINFO_CONFIG,
} from '../constants/network';

// Internal state
let currentState = {
  status: NETWORK_STATUS.UNKNOWN,
  isConnected: null,
  isInternetReachable: null,
  connectionType: CONNECTION_TYPE.UNKNOWN,
  details: null,
  lastCheckedAt: null,
};

let subscribers = [];
let unsubscribeNetInfo = null;
let debounceTimer = null;
let initialCheckTimer = null;
let isInitialized = false;

/**
 * Debounce helper to prevent rapid state changes
 */
const debounce = (fn, delay) => {
  return (...args) => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }
    debounceTimer = setTimeout(() => {
      debounceTimer = null;
      fn(...args);
    }, delay);
  };
};

/**
 * Notify all subscribers of state change
 */
const notifySubscribers = (state) => {
  subscribers.forEach((callback) => {
    try {
      callback(state);
    } catch (error) {
      logError(error, 'NetworkService.notifySubscribers');
    }
  });
};

/**
 * Determine network status from NetInfo state
 * Handles the tricky null states gracefully
 */
const determineNetworkStatus = (netInfoState) => {
  const { isConnected, isInternetReachable } = netInfoState;

  // If we know for certain internet is reachable
  if (isInternetReachable === true) {
    return NETWORK_STATUS.ONLINE;
  }

  // If we know for certain internet is NOT reachable
  if (isInternetReachable === false) {
    return NETWORK_STATUS.OFFLINE;
  }

  // isInternetReachable is null (unknown)
  // Fall back to isConnected, but treat as UNKNOWN if also null
  if (isConnected === true) {
    // Connected to network but internet status unknown
    // This is the "optimistic" case - assume online until proven otherwise
    return NETWORK_STATUS.UNKNOWN;
  }

  if (isConnected === false) {
    return NETWORK_STATUS.OFFLINE;
  }

  // Both are null - truly unknown state
  return NETWORK_STATUS.UNKNOWN;
};

/**
 * Map NetInfo type to our connection type
 */
const mapConnectionType = (type) => {
  const typeMap = {
    wifi: CONNECTION_TYPE.WIFI,
    cellular: CONNECTION_TYPE.CELLULAR,
    ethernet: CONNECTION_TYPE.ETHERNET,
    bluetooth: CONNECTION_TYPE.BLUETOOTH,
    vpn: CONNECTION_TYPE.VPN,
    none: CONNECTION_TYPE.NONE,
    unknown: CONNECTION_TYPE.UNKNOWN,
    other: CONNECTION_TYPE.OTHER,
  };
  return typeMap[type] || CONNECTION_TYPE.UNKNOWN;
};

/**
 * Process NetInfo state update
 */
const processNetInfoState = (netInfoState) => {
  const newState = {
    status: determineNetworkStatus(netInfoState),
    isConnected: netInfoState.isConnected,
    isInternetReachable: netInfoState.isInternetReachable,
    connectionType: mapConnectionType(netInfoState.type),
    details: netInfoState.details || null,
    lastCheckedAt: Date.now(),
  };

  // Check if state actually changed (avoid unnecessary updates)
  const hasChanged =
    currentState.status !== newState.status ||
    currentState.isConnected !== newState.isConnected ||
    currentState.isInternetReachable !== newState.isInternetReachable ||
    currentState.connectionType !== newState.connectionType;

  if (hasChanged) {
    currentState = newState;
    notifySubscribers(currentState);
  }

  return currentState;
};

/**
 * Debounced state processor to handle rapid network changes
 */
const debouncedProcessState = debounce((netInfoState) => {
  processNetInfoState(netInfoState);
}, NETWORK_TIMEOUTS.DEBOUNCE_MS);

/**
 * Handle NetInfo state change
 */
const handleNetInfoChange = (netInfoState) => {
  // For significant changes (online <-> offline), process immediately
  const currentlyOnline = currentState.status === NETWORK_STATUS.ONLINE;
  const newStatus = determineNetworkStatus(netInfoState);
  const significantChange =
    (currentlyOnline && newStatus === NETWORK_STATUS.OFFLINE) ||
    (!currentlyOnline && newStatus === NETWORK_STATUS.ONLINE);

  if (significantChange) {
    // Clear any pending debounced update
    if (debounceTimer) {
      clearTimeout(debounceTimer);
      debounceTimer = null;
    }
    processNetInfoState(netInfoState);
  } else {
    // Minor changes (type changes, details) get debounced
    debouncedProcessState(netInfoState);
  }
};

/**
 * Initialize the network service
 * Sets up NetInfo listener and performs initial check
 */
export const initialize = async () => {
  if (isInitialized) {
    return currentState;
  }

  try {
    // Configure NetInfo
    NetInfo.configure(NETINFO_CONFIG);

    // Get initial state
    const initialState = await NetInfo.fetch();
    processNetInfoState(initialState);

    // If initial state is UNKNOWN, set a timer to resolve it
    // This handles the case where isInternetReachable starts as null
    if (currentState.status === NETWORK_STATUS.UNKNOWN) {
      initialCheckTimer = setTimeout(() => {
        // If still unknown after delay, do a refresh
        if (currentState.status === NETWORK_STATUS.UNKNOWN) {
          refresh();
        }
      }, NETWORK_TIMEOUTS.INITIAL_CHECK_DELAY_MS);
    }

    // Subscribe to changes
    unsubscribeNetInfo = NetInfo.addEventListener(handleNetInfoChange);

    isInitialized = true;
    return currentState;
  } catch (error) {
    logError(error, 'NetworkService.initialize');
    // Return a safe default state on initialization failure
    currentState = {
      status: NETWORK_STATUS.UNKNOWN,
      isConnected: null,
      isInternetReachable: null,
      connectionType: CONNECTION_TYPE.UNKNOWN,
      details: null,
      lastCheckedAt: Date.now(),
    };
    isInitialized = true; // Mark as initialized to prevent retry loops
    return currentState;
  }
};

/**
 * Get current network state
 */
export const getNetworkState = () => {
  return { ...currentState };
};

/**
 * Check if currently online (convenience method)
 */
export const isOnline = () => {
  return currentState.status === NETWORK_STATUS.ONLINE;
};

/**
 * Check if status is known (not in initial unknown state)
 */
export const isStatusKnown = () => {
  return currentState.status !== NETWORK_STATUS.UNKNOWN;
};

/**
 * Subscribe to network state changes
 * @param {Function} callback - Called with new state on changes
 * @returns {Function} - Unsubscribe function
 */
export const subscribe = (callback) => {
  if (typeof callback !== 'function') {
    throw new Error('Callback must be a function');
  }

  subscribers.push(callback);

  // Immediately call with current state
  try {
    callback(currentState);
  } catch (error) {
    logError(error, 'NetworkService.subscribe.initialCallback');
  }

  // Return unsubscribe function
  return () => {
    const index = subscribers.indexOf(callback);
    if (index > -1) {
      subscribers.splice(index, 1);
    }
  };
};

/**
 * Force a network state refresh
 * Useful when you suspect the cached state might be stale
 */
export const refresh = async () => {
  try {
    const freshState = await NetInfo.refresh();
    return processNetInfoState(freshState);
  } catch (error) {
    logError(error, 'NetworkService.refresh');
    return currentState;
  }
};

/**
 * Check if our own API backend is reachable
 * This is a more reliable check than just internet reachability
 * because it verifies we can actually reach our servers
 *
 * @returns {Promise<{reachable: boolean, latency: number|null, error: string|null}>}
 */
export const checkApiReachability = async () => {
  const startTime = Date.now();

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      NETWORK_TIMEOUTS.API_PING_TIMEOUT_MS
    );

    // Use a lightweight endpoint - just need to know if server responds
    // Most APIs have a health check endpoint; fall back to base URL
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'HEAD',
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const latency = Date.now() - startTime;

    // Any response (even 404) means we reached the server
    return {
      reachable: true,
      latency,
      error: null,
    };
  } catch (error) {
    const latency = Date.now() - startTime;

    // Distinguish between timeout and other errors
    if (error.name === 'AbortError') {
      return {
        reachable: false,
        latency,
        error: 'Request timed out',
      };
    }

    return {
      reachable: false,
      latency: null,
      error: error.message || 'Failed to reach API',
    };
  }
};

/**
 * Perform a comprehensive connectivity check
 * Combines NetInfo state with an API ping for maximum reliability
 *
 * @returns {Promise<{status: string, apiReachable: boolean, details: object}>}
 */
export const performFullConnectivityCheck = async () => {
  // First refresh NetInfo state
  const netState = await refresh();

  // If NetInfo says we're offline, trust it
  if (netState.status === NETWORK_STATUS.OFFLINE) {
    return {
      status: NETWORK_STATUS.OFFLINE,
      apiReachable: false,
      details: {
        netInfoStatus: netState.status,
        connectionType: netState.connectionType,
      },
    };
  }

  // If NetInfo says online or unknown, verify with API ping
  const apiCheck = await checkApiReachability();

  return {
    status: apiCheck.reachable ? NETWORK_STATUS.ONLINE : NETWORK_STATUS.OFFLINE,
    apiReachable: apiCheck.reachable,
    details: {
      netInfoStatus: netState.status,
      connectionType: netState.connectionType,
      apiLatency: apiCheck.latency,
      apiError: apiCheck.error,
    },
  };
};

/**
 * Clean up the network service
 * Call this when the app is shutting down or you want to stop monitoring
 */
export const cleanup = () => {
  if (unsubscribeNetInfo) {
    unsubscribeNetInfo();
    unsubscribeNetInfo = null;
  }

  if (debounceTimer) {
    clearTimeout(debounceTimer);
    debounceTimer = null;
  }

  if (initialCheckTimer) {
    clearTimeout(initialCheckTimer);
    initialCheckTimer = null;
  }

  subscribers = [];
  isInitialized = false;

  // Reset state
  currentState = {
    status: NETWORK_STATUS.UNKNOWN,
    isConnected: null,
    isInternetReachable: null,
    connectionType: CONNECTION_TYPE.UNKNOWN,
    details: null,
    lastCheckedAt: null,
  };
};

/**
 * Check if service is initialized
 */
export const isServiceInitialized = () => {
  return isInitialized;
};

// For testing purposes - allows resetting internal state
export const _resetForTesting = () => {
  cleanup();
};

// For testing purposes - allows simulating state changes
export const _simulateStateChange = (mockState) => {
  if (process.env.NODE_ENV === 'test') {
    processNetInfoState(mockState);
  }
};
