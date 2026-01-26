/**
 * CircleHeader Component
 * Displays circle name, member avatars, and settings button
 * Used at the top of CircleFeedScreen
 */
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../../styles/theme';

export default function CircleHeader({
  circle,
  onSettingsPress,
  onMembersPress,
}) {
  if (!circle) return null;

  const members = circle.members || [];
  const memberCount = members.length;
  const displayMembers = members.slice(0, 4); // Show max 4 avatars

  return (
    <View style={styles.container}>
      <View style={styles.mainRow}>
        {/* Circle Icon & Name */}
        <View style={styles.titleSection}>
          <View style={styles.iconContainer}>
            <Ionicons name="people" size={20} color={COLORS.primary} />
          </View>
          <View style={styles.titleContent}>
            <Text style={styles.circleName} numberOfLines={1}>
              {circle.name}
            </Text>
            {circle.description ? (
              <Text style={styles.description} numberOfLines={1}>
                {circle.description}
              </Text>
            ) : null}
          </View>
        </View>

        {/* Settings Button */}
        <TouchableOpacity
          style={styles.settingsButton}
          onPress={onSettingsPress}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <Ionicons name="settings-outline" size={22} color={COLORS.primary} />
        </TouchableOpacity>
      </View>

      {/* Members Row */}
      <TouchableOpacity
        style={styles.membersRow}
        onPress={onMembersPress}
        activeOpacity={0.7}
      >
        {/* Avatar Stack */}
        <View style={styles.avatarStack}>
          {displayMembers.map((member, index) => (
            <View
              key={member.user_id || index}
              style={[
                styles.avatar,
                { marginLeft: index > 0 ? -8 : 0, zIndex: displayMembers.length - index }
              ]}
            >
              <Text style={styles.avatarText}>
                {(member.username || 'U')[0].toUpperCase()}
              </Text>
            </View>
          ))}
          {memberCount > 4 && (
            <View style={[styles.avatar, styles.moreAvatar, { marginLeft: -8 }]}>
              <Text style={styles.moreText}>+{memberCount - 4}</Text>
            </View>
          )}
        </View>

        {/* Member Count */}
        <Text style={styles.memberCount}>
          {memberCount} {memberCount === 1 ? 'member' : 'members'}
        </Text>

        <Ionicons name="chevron-forward" size={16} color={COLORS.textLight} />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.card,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
    ...SHADOWS.small,
  },
  mainRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  titleSection: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.sm,
  },
  titleContent: {
    flex: 1,
  },
  circleName: {
    ...TYPOGRAPHY.heading,
    fontSize: 18,
    color: COLORS.text,
  },
  description: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginTop: 1,
  },
  settingsButton: {
    padding: SPACING.xs,
  },
  membersRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: SPACING.sm,
    paddingTop: SPACING.sm,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  avatarStack: {
    flexDirection: 'row',
    marginRight: SPACING.sm,
  },
  avatar: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: COLORS.accent,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: COLORS.card,
  },
  avatarText: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.white,
  },
  moreAvatar: {
    backgroundColor: COLORS.secondary,
  },
  moreText: {
    fontSize: 10,
    fontWeight: '600',
    color: COLORS.white,
  },
  memberCount: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    flex: 1,
  },
});
