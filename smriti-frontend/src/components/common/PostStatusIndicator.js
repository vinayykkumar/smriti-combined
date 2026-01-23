/**
 * PostStatusIndicator - Shows sync status for queued/pending posts.
 *
 * Displays visual indicators:
 * - Syncing: Spinner with "Syncing..."
 * - Pending: Clock icon with "Pending"
 * - Failed: Error icon with "Failed to sync" and retry button
 */
import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING } from '../../styles/theme';

/**
 * Sync status types
 */
export const SYNC_STATUS = {
  SYNCED: 'synced',
  SYNCING: 'syncing',
  PENDING: 'pending',
  FAILED: 'failed',
};

/**
 * PostStatusIndicator component
 *
 * @param {object} props
 * @param {string} props.status - Current sync status
 * @param {Function} props.onRetry - Callback when retry is pressed (for failed status)
 * @param {boolean} props.compact - Use compact styling
 */
export function PostStatusIndicator({ status, onRetry, compact = false }) {
  // Don't render anything for synced posts
  if (status === SYNC_STATUS.SYNCED || !status) {
    return null;
  }

  const renderContent = () => {
    switch (status) {
      case SYNC_STATUS.SYNCING:
        return (
          <View style={[styles.container, compact && styles.containerCompact]}>
            <ActivityIndicator size="small" color={COLORS.primary} />
            <Text style={[styles.text, styles.syncingText, compact && styles.textCompact]}>
              Syncing...
            </Text>
          </View>
        );

      case SYNC_STATUS.PENDING:
        return (
          <View style={[styles.container, compact && styles.containerCompact]}>
            <Ionicons
              name="time-outline"
              size={compact ? 14 : 16}
              color="#8B7355"
            />
            <Text style={[styles.text, styles.pendingText, compact && styles.textCompact]}>
              Pending
            </Text>
          </View>
        );

      case SYNC_STATUS.FAILED:
        return (
          <View style={[styles.container, styles.failedContainer, compact && styles.containerCompact]}>
            <Ionicons
              name="alert-circle-outline"
              size={compact ? 14 : 16}
              color="#C75050"
            />
            <Text style={[styles.text, styles.failedText, compact && styles.textCompact]}>
              Failed to sync
            </Text>
            {onRetry && (
              <TouchableOpacity
                onPress={onRetry}
                style={[styles.retryButton, compact && styles.retryButtonCompact]}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                <Ionicons
                  name="refresh-outline"
                  size={compact ? 14 : 16}
                  color="#5C4033"
                />
                {!compact && <Text style={styles.retryText}>Retry</Text>}
              </TouchableOpacity>
            )}
          </View>
        );

      default:
        return null;
    }
  };

  return renderContent();
}

/**
 * PostStatusBadge - Smaller badge version for list items
 */
export function PostStatusBadge({ status }) {
  if (status === SYNC_STATUS.SYNCED || !status) {
    return null;
  }

  const getBadgeConfig = () => {
    switch (status) {
      case SYNC_STATUS.SYNCING:
        return {
          backgroundColor: 'rgba(139, 115, 85, 0.15)',
          color: '#8B7355',
          icon: null,
          showSpinner: true,
          label: 'Syncing',
        };
      case SYNC_STATUS.PENDING:
        return {
          backgroundColor: 'rgba(139, 115, 85, 0.1)',
          color: '#8B7355',
          icon: 'time-outline',
          showSpinner: false,
          label: 'Offline',
        };
      case SYNC_STATUS.FAILED:
        return {
          backgroundColor: 'rgba(199, 80, 80, 0.1)',
          color: '#C75050',
          icon: 'alert-circle',
          showSpinner: false,
          label: 'Failed',
        };
      default:
        return null;
    }
  };

  const config = getBadgeConfig();
  if (!config) return null;

  return (
    <View style={[styles.badge, { backgroundColor: config.backgroundColor }]}>
      {config.showSpinner ? (
        <ActivityIndicator size={10} color={config.color} />
      ) : config.icon ? (
        <Ionicons name={config.icon} size={10} color={config.color} />
      ) : null}
      <Text style={[styles.badgeText, { color: config.color }]}>
        {config.label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.xs,
    paddingHorizontal: SPACING.sm,
    backgroundColor: 'rgba(255, 255, 255, 0.6)',
    borderRadius: 12,
    gap: 6,
  },
  containerCompact: {
    paddingVertical: 4,
    paddingHorizontal: 8,
    gap: 4,
  },
  failedContainer: {
    backgroundColor: 'rgba(199, 80, 80, 0.08)',
  },
  text: {
    fontSize: 13,
    fontWeight: '500',
  },
  textCompact: {
    fontSize: 11,
  },
  syncingText: {
    color: COLORS.primary || '#5C4033',
  },
  pendingText: {
    color: '#8B7355',
  },
  failedText: {
    color: '#C75050',
  },
  retryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: SPACING.xs,
    paddingVertical: 4,
    paddingHorizontal: 8,
    backgroundColor: 'rgba(92, 64, 51, 0.1)',
    borderRadius: 8,
    gap: 4,
  },
  retryButtonCompact: {
    paddingVertical: 2,
    paddingHorizontal: 6,
    marginLeft: 4,
  },
  retryText: {
    fontSize: 12,
    color: '#5C4033',
    fontWeight: '600',
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 2,
    paddingHorizontal: 6,
    borderRadius: 4,
    gap: 3,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '600',
  },
});

export default PostStatusIndicator;
