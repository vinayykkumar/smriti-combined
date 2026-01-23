import { useContext } from 'react';
import { NetworkContext } from '../contexts/NetworkContext';

/**
 * useNetwork - Hook for accessing network state from any component
 *
 * Provides easy access to network connectivity status, connection type,
 * and methods for checking connectivity.
 *
 * @example
 * // Basic usage
 * const { isOnline, isOffline } = useNetwork();
 *
 * if (isOffline) {
 *   showOfflineMessage();
 * }
 *
 * @example
 * // Check before making API call
 * const { isOnline, checkApiReachability } = useNetwork();
 *
 * const handleSubmit = async () => {
 *   if (!isOnline) {
 *     queueForLater();
 *     return;
 *   }
 *   // proceed with API call
 * };
 *
 * @example
 * // Get connection details
 * const { connectionType, connectionDetails } = useNetwork();
 * console.log(`Connected via ${connectionType}`);
 *
 * @returns {object} Network state and methods
 */
export function useNetwork() {
  const context = useContext(NetworkContext);

  if (!context) {
    throw new Error(
      'useNetwork must be used within a NetworkProvider. ' +
        'Wrap your app with <NetworkProvider> to use this hook.'
    );
  }

  return context;
}

/**
 * useIsOnline - Simplified hook that just returns online status
 *
 * Use this when you only need to check if the device is online
 * and don't need other network details.
 *
 * @example
 * const isOnline = useIsOnline();
 *
 * @returns {boolean} True if online, false otherwise
 */
export function useIsOnline() {
  const { isOnline } = useNetwork();
  return isOnline;
}

/**
 * useConnectionType - Hook that returns the current connection type
 *
 * @example
 * const connectionType = useConnectionType();
 * // 'wifi', 'cellular', 'ethernet', 'none', 'unknown', etc.
 *
 * @returns {string} Connection type
 */
export function useConnectionType() {
  const { connectionType } = useNetwork();
  return connectionType;
}
