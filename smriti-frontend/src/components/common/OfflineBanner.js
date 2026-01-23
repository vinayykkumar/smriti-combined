import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNetwork } from '../../hooks/useNetwork';
import { COLORS, SPACING } from '../../styles/theme';

/**
 * OfflineBanner - A non-intrusive banner that shows when the user is offline.
 *
 * - Only shows when definitively offline (not during initial UNKNOWN state)
 * - Appears at the top of the screen
 * - Minimal design that doesn't distract from the main content
 */
export default function OfflineBanner() {
  const { isOffline, isStatusKnown } = useNetwork();

  // Don't show during initial check (UNKNOWN state)
  // Only show when we're certain the user is offline
  if (!isStatusKnown || !isOffline) {
    return null;
  }

  return (
    <View style={styles.container}>
      <Ionicons
        name="cloud-offline-outline"
        size={16}
        color={COLORS.white}
        style={styles.icon}
      />
      <Text style={styles.text}>You're offline</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.error,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.md,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    marginRight: SPACING.xs,
  },
  text: {
    color: COLORS.white,
    fontSize: 14,
    fontWeight: '500',
  },
});
