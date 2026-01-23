/**
 * Network-related constants for connectivity monitoring.
 */

// Network status values
export const NETWORK_STATUS = {
  ONLINE: 'online',
  OFFLINE: 'offline',
  UNKNOWN: 'unknown', // Initial state before first check completes
};

// Connection types from NetInfo
export const CONNECTION_TYPE = {
  WIFI: 'wifi',
  CELLULAR: 'cellular',
  ETHERNET: 'ethernet',
  BLUETOOTH: 'bluetooth',
  VPN: 'vpn',
  NONE: 'none',
  UNKNOWN: 'unknown',
  OTHER: 'other',
};

// Cellular generations
export const CELLULAR_GENERATION = {
  '2G': '2g',
  '3G': '3g',
  '4G': '4g',
  '5G': '5g',
};

// Timing constants (in milliseconds)
export const NETWORK_TIMEOUTS = {
  DEBOUNCE_MS: 300,              // Debounce rapid network changes
  API_PING_TIMEOUT_MS: 5000,     // Timeout for API reachability check
  REACHABILITY_SHORT_MS: 5000,   // NetInfo check interval when unreachable
  REACHABILITY_LONG_MS: 60000,   // NetInfo check interval when reachable
  INITIAL_CHECK_DELAY_MS: 1000,  // Delay before treating null as offline
};

// NetInfo configuration
export const NETINFO_CONFIG = {
  reachabilityUrl: 'https://clients3.google.com/generate_204',
  reachabilityShortTimeout: NETWORK_TIMEOUTS.REACHABILITY_SHORT_MS,
  reachabilityLongTimeout: NETWORK_TIMEOUTS.REACHABILITY_LONG_MS,
  reachabilityRequestTimeout: NETWORK_TIMEOUTS.API_PING_TIMEOUT_MS,
};
