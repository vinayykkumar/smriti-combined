/**
 * CircleCard Component
 * Displays a circle in the list with name, description, and member count
 */
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../../styles/theme';

export default function CircleCard({ circle, onPress }) {
  const memberCount = circle.members?.length || 0;

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={() => onPress?.(circle)}
      activeOpacity={0.7}
    >
      <View style={styles.iconContainer}>
        <Ionicons name="people" size={24} color={COLORS.primary} />
      </View>

      <View style={styles.content}>
        <Text style={styles.name} numberOfLines={1}>
          {circle.name}
        </Text>
        {circle.description ? (
          <Text style={styles.description} numberOfLines={2}>
            {circle.description}
          </Text>
        ) : null}
        <View style={styles.metaRow}>
          <Ionicons name="person-outline" size={14} color={COLORS.textLight} />
          <Text style={styles.memberCount}>
            {memberCount} {memberCount === 1 ? 'member' : 'members'}
          </Text>
        </View>
      </View>

      <Ionicons name="chevron-forward" size={20} color={COLORS.textLight} />
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    borderRadius: 12,
    padding: SPACING.md,
    marginHorizontal: SPACING.md,
    marginVertical: SPACING.xs,
    ...SHADOWS.small,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.md,
  },
  content: {
    flex: 1,
    marginRight: SPACING.sm,
  },
  name: {
    ...TYPOGRAPHY.body,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 2,
  },
  description: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginBottom: SPACING.xs,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  memberCount: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginLeft: 4,
  },
});
