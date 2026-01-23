import React, { createContext, useState, useEffect, useCallback, useRef } from 'react';
import * as networkService from '../services/networkService';
import { NETWORK_STATUS } from '../constants/network';
import { logError } from '../utils/errorHandler';

// Create the Network Context
export const NetworkContext = createContext();

/**
 * Default network state - used before initialization completes
 */
const defaultNetworkState = {
  status: NETWORK_STATUS.UNKNOWN,
  isConnected: null,
  isInternetReachable: null,
  connectionType: 'unknown',
  details: null,
  lastCheckedAt: null,
};

/**
 * NetworkProvider - Provides network state to the entire app
 *
 * Wraps the networkService and manages its lifecycle.
 * Provides network status, connection info, and helper methods to children.
 */
export function NetworkProvider({ children }) {
  const [networkState, setNetworkState] = useState(defaultNetworkState);
  const [isInitializing, setIsInitializing] = useState(true);
  const unsubscribeRef = useRef(null);
  const isMountedRef = useRef(true);

  /**
   * Handle network state changes from the service
   */
  const handleNetworkStateChange = useCallback((newState) => {
    if (isMountedRef.current) {
      setNetworkState(newState);
    }
  }, []);

  /**
   * Initialize the network service on mount
   */
  useEffect(() => {
    isMountedRef.current = true;

    const initializeNetwork = async () => {
      try {
        // Initialize the service
        await networkService.initialize();

        // Subscribe to state changes
        unsubscribeRef.current = networkService.subscribe(handleNetworkStateChange);
      } catch (error) {
        logError(error, 'NetworkContext.initialize');
        // Set a safe default state on error
        if (isMountedRef.current) {
          setNetworkState({
            ...defaultNetworkState,
            status: NETWORK_STATUS.UNKNOWN,
          });
        }
      } finally {
        if (isMountedRef.current) {
          setIsInitializing(false);
        }
      }
    };

    initializeNetwork();

    // Cleanup on unmount
    return () => {
      isMountedRef.current = false;

      if (unsubscribeRef.current) {
        unsubscribeRef.current();
        unsubscribeRef.current = null;
      }

      networkService.cleanup();
    };
  }, [handleNetworkStateChange]);

  /**
   * Force refresh network state
   */
  const refresh = useCallback(async () => {
    try {
      return await networkService.refresh();
    } catch (error) {
      logError(error, 'NetworkContext.refresh');
      return networkState;
    }
  }, [networkState]);

  /**
   * Check if our API is reachable
   */
  const checkApiReachability = useCallback(async () => {
    try {
      return await networkService.checkApiReachability();
    } catch (error) {
      logError(error, 'NetworkContext.checkApiReachability');
      return { reachable: false, latency: null, error: error.message };
    }
  }, []);

  /**
   * Perform full connectivity check (NetInfo + API ping)
   */
  const performFullConnectivityCheck = useCallback(async () => {
    try {
      return await networkService.performFullConnectivityCheck();
    } catch (error) {
      logError(error, 'NetworkContext.performFullConnectivityCheck');
      return {
        status: NETWORK_STATUS.UNKNOWN,
        apiReachable: false,
        details: { error: error.message },
      };
    }
  }, []);

  // Derive convenience booleans from state
  const isOnline = networkState.status === NETWORK_STATUS.ONLINE;
  const isOffline = networkState.status === NETWORK_STATUS.OFFLINE;
  const isStatusKnown = networkState.status !== NETWORK_STATUS.UNKNOWN;

  const value = {
    // Current state
    networkState,
    isInitializing,

    // Convenience booleans
    isOnline,
    isOffline,
    isStatusKnown,

    // Connection details
    connectionType: networkState.connectionType,
    connectionDetails: networkState.details,

    // Methods
    refresh,
    checkApiReachability,
    performFullConnectivityCheck,
  };

  return (
    <NetworkContext.Provider value={value}>
      {children}
    </NetworkContext.Provider>
  );
}
