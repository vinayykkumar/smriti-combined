/**
 * CircleSettingsScreen
 * Circle settings: members list, invite code, delete voting
 * Note: Users cannot leave circles - only unanimous delete is possible
 */
import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Share,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../styles/theme';
import * as circlesApi from '../services/api/circles';
import { useAuth } from '../hooks/useAuth';

export default function CircleSettingsScreen({ route, navigation }) {
  const { circleId, circleName } = route.params;
  const { user } = useAuth();

  const [circle, setCircle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [voting, setVoting] = useState(false);

  // Load circle details
  const loadCircle = useCallback(async () => {
    try {
      const data = await circlesApi.getCircleDetails(circleId);
      setCircle(data);
    } catch (err) {
      Alert.alert('Error', err.message || 'Failed to load circle');
    } finally {
      setLoading(false);
    }
  }, [circleId]);

  useFocusEffect(
    useCallback(() => {
      loadCircle();
    }, [loadCircle])
  );

  useEffect(() => {
    navigation.setOptions({
      headerTitle: 'Circle Settings',
    });
  }, [navigation]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadCircle();
    setRefreshing(false);
  };

  // Share invite code
  const handleShareInvite = async () => {
    if (!circle?.invite_code) return;

    try {
      await Share.share({
        message: `Join my circle "${circle.name}" on Smriti!\n\nInvite code: ${circle.invite_code}`,
      });
    } catch (err) {
      console.error('Share failed:', err);
    }
  };

  // Regenerate invite code
  const handleRegenerateCode = async () => {
    Alert.alert(
      'Regenerate Invite Code?',
      'The current invite code will stop working. Anyone with the old code won\'t be able to join.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Regenerate',
          style: 'destructive',
          onPress: async () => {
            setRegenerating(true);
            try {
              const newCode = await circlesApi.regenerateInviteCode(circleId);
              if (newCode) {
                setCircle(prev => ({ ...prev, invite_code: newCode }));
                Alert.alert('Success', 'New invite code generated');
              }
            } catch (err) {
              Alert.alert('Error', err.message || 'Failed to regenerate code');
            } finally {
              setRegenerating(false);
            }
          },
        },
      ]
    );
  };

  // Check if current user has voted for deletion
  const hasVotedForDeletion = () => {
    if (!circle?.deletion_votes || !user) return false;
    return circle.deletion_votes.some(
      vote => vote.user_id === user.id || vote.user_id === user._id
    );
  };

  // Vote to delete circle
  const handleVoteDelete = async () => {
    const memberCount = circle?.members?.length || 0;
    const currentVotes = circle?.deletion_votes?.length || 0;
    const votesNeeded = memberCount - currentVotes - 1;

    Alert.alert(
      'Vote to Delete Circle?',
      votesNeeded > 0
        ? `This requires unanimous consent. ${votesNeeded} more ${votesNeeded === 1 ? 'vote is' : 'votes are'} needed after yours.`
        : 'You are the last vote needed. The circle will be permanently deleted.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Vote to Delete',
          style: 'destructive',
          onPress: async () => {
            setVoting(true);
            try {
              const result = await circlesApi.voteToDeleteCircle(circleId);
              if (result?.deleted) {
                Alert.alert('Circle Deleted', 'The circle has been permanently deleted.', [
                  { text: 'OK', onPress: () => navigation.navigate('CirclesList') },
                ]);
              } else {
                await loadCircle();
                Alert.alert('Vote Recorded', 'Your vote to delete has been recorded.');
              }
            } catch (err) {
              Alert.alert('Error', err.message || 'Failed to record vote');
            } finally {
              setVoting(false);
            }
          },
        },
      ]
    );
  };

  // Revoke deletion vote
  const handleRevokeVote = async () => {
    Alert.alert(
      'Revoke Delete Vote?',
      'Your vote to delete this circle will be removed.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Revoke Vote',
          onPress: async () => {
            setVoting(true);
            try {
              await circlesApi.revokeDeleteVote(circleId);
              await loadCircle();
              Alert.alert('Vote Revoked', 'Your deletion vote has been removed.');
            } catch (err) {
              Alert.alert('Error', err.message || 'Failed to revoke vote');
            } finally {
              setVoting(false);
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  if (!circle) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="alert-circle-outline" size={48} color={COLORS.error} />
        <Text style={styles.errorText}>Circle not found</Text>
      </View>
    );
  }

  const members = circle.members || [];
  const deletionVotes = circle.deletion_votes || [];
  const userHasVoted = hasVotedForDeletion();

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={handleRefresh}
          tintColor={COLORS.primary}
        />
      }
    >
      {/* Circle Info Section */}
      <View style={styles.section}>
        <View style={styles.circleInfoHeader}>
          <View style={styles.circleIcon}>
            <Ionicons name="people" size={28} color={COLORS.primary} />
          </View>
          <View style={styles.circleInfoContent}>
            <Text style={styles.circleName}>{circle.name}</Text>
            {circle.description ? (
              <Text style={styles.circleDescription}>{circle.description}</Text>
            ) : null}
          </View>
        </View>
      </View>

      {/* Invite Code Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Invite Code</Text>
        <View style={styles.inviteCard}>
          <Text style={styles.inviteCode}>{circle.invite_code}</Text>
          <View style={styles.inviteActions}>
            <TouchableOpacity style={styles.inviteButton} onPress={handleShareInvite}>
              <Ionicons name="share-outline" size={18} color={COLORS.card} />
              <Text style={styles.inviteButtonText}>Share</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.inviteButton, styles.inviteButtonSecondary]}
              onPress={handleRegenerateCode}
              disabled={regenerating}
            >
              {regenerating ? (
                <ActivityIndicator size="small" color={COLORS.primary} />
              ) : (
                <>
                  <Ionicons name="refresh-outline" size={18} color={COLORS.primary} />
                  <Text style={styles.inviteButtonTextSecondary}>New Code</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        </View>
        <Text style={styles.inviteHint}>
          Share this code with people you want to invite. Max 5 members per circle.
        </Text>
      </View>

      {/* Members Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          Members ({members.length}/5)
        </Text>
        <View style={styles.membersList}>
          {members.map((member, index) => (
            <View key={member.user_id || index} style={styles.memberItem}>
              <View style={styles.memberAvatar}>
                <Text style={styles.memberAvatarText}>
                  {(member.username || 'U')[0].toUpperCase()}
                </Text>
              </View>
              <View style={styles.memberInfo}>
                <Text style={styles.memberName}>{member.username}</Text>
                <Text style={styles.memberJoined}>
                  Joined {new Date(member.joined_at).toLocaleDateString()}
                </Text>
              </View>
              {/* Show if member voted for deletion */}
              {deletionVotes.some(v => v.user_id === member.user_id) && (
                <View style={styles.deletionBadge}>
                  <Ionicons name="close-circle" size={16} color={COLORS.error} />
                </View>
              )}
            </View>
          ))}
        </View>
      </View>

      {/* Deletion Votes Section (if any) */}
      {deletionVotes.length > 0 && (
        <View style={styles.section}>
          <View style={styles.warningCard}>
            <Ionicons name="warning-outline" size={24} color={COLORS.error} />
            <View style={styles.warningContent}>
              <Text style={styles.warningTitle}>Deletion in Progress</Text>
              <Text style={styles.warningText}>
                {deletionVotes.length} of {members.length} members have voted to delete.
                {members.length - deletionVotes.length > 0
                  ? ` ${members.length - deletionVotes.length} more needed.`
                  : ' Circle will be deleted.'}
              </Text>
            </View>
          </View>
        </View>
      )}

      {/* Danger Zone */}
      <View style={[styles.section, styles.dangerSection]}>
        <Text style={[styles.sectionTitle, styles.dangerTitle]}>Danger Zone</Text>
        <Text style={styles.dangerDescription}>
          Circles cannot be left. They can only be deleted with unanimous consent from all members.
        </Text>

        {userHasVoted ? (
          <TouchableOpacity
            style={styles.revokeButton}
            onPress={handleRevokeVote}
            disabled={voting}
          >
            {voting ? (
              <ActivityIndicator size="small" color={COLORS.secondary} />
            ) : (
              <>
                <Ionicons name="arrow-undo-outline" size={18} color={COLORS.secondary} />
                <Text style={styles.revokeButtonText}>Revoke My Delete Vote</Text>
              </>
            )}
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={handleVoteDelete}
            disabled={voting}
          >
            {voting ? (
              <ActivityIndicator size="small" color={COLORS.card} />
            ) : (
              <>
                <Ionicons name="trash-outline" size={18} color={COLORS.card} />
                <Text style={styles.deleteButtonText}>Vote to Delete Circle</Text>
              </>
            )}
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  content: {
    padding: SPACING.md,
    paddingBottom: SPACING.xxl,
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    ...TYPOGRAPHY.body,
    color: COLORS.error,
    marginTop: SPACING.md,
  },
  section: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: SPACING.md,
    marginBottom: SPACING.md,
    ...SHADOWS.small,
  },
  sectionTitle: {
    ...TYPOGRAPHY.body,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: SPACING.md,
  },
  circleInfoHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  circleIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.md,
  },
  circleInfoContent: {
    flex: 1,
  },
  circleName: {
    ...TYPOGRAPHY.heading,
    color: COLORS.text,
  },
  circleDescription: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginTop: 2,
  },
  inviteCard: {
    backgroundColor: COLORS.background,
    borderRadius: 12,
    padding: SPACING.md,
    alignItems: 'center',
  },
  inviteCode: {
    fontSize: 32,
    fontWeight: '700',
    letterSpacing: 6,
    color: COLORS.text,
    marginBottom: SPACING.md,
  },
  inviteActions: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  inviteButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 8,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.md,
    flexDirection: 'row',
    alignItems: 'center',
  },
  inviteButtonSecondary: {
    backgroundColor: COLORS.card,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  inviteButtonText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.card,
    fontWeight: '600',
    marginLeft: 4,
  },
  inviteButtonTextSecondary: {
    ...TYPOGRAPHY.caption,
    color: COLORS.primary,
    fontWeight: '600',
    marginLeft: 4,
  },
  inviteHint: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    textAlign: 'center',
    marginTop: SPACING.sm,
    fontStyle: 'italic',
  },
  membersList: {
    gap: SPACING.sm,
  },
  memberItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.background,
    borderRadius: 12,
    padding: SPACING.sm,
  },
  memberAvatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: COLORS.accent,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.sm,
  },
  memberAvatarText: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.white,
  },
  memberInfo: {
    flex: 1,
  },
  memberName: {
    ...TYPOGRAPHY.body,
    fontWeight: '500',
    color: COLORS.text,
  },
  memberJoined: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
  },
  deletionBadge: {
    padding: SPACING.xs,
  },
  warningCard: {
    flexDirection: 'row',
    backgroundColor: 'rgba(193, 74, 57, 0.1)',
    borderRadius: 12,
    padding: SPACING.md,
    borderWidth: 1,
    borderColor: 'rgba(193, 74, 57, 0.2)',
  },
  warningContent: {
    flex: 1,
    marginLeft: SPACING.sm,
  },
  warningTitle: {
    ...TYPOGRAPHY.body,
    fontWeight: '600',
    color: COLORS.error,
  },
  warningText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.error,
    marginTop: 2,
  },
  dangerSection: {
    borderWidth: 1,
    borderColor: 'rgba(193, 74, 57, 0.3)',
  },
  dangerTitle: {
    color: COLORS.error,
  },
  dangerDescription: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginBottom: SPACING.md,
    lineHeight: 18,
  },
  deleteButton: {
    backgroundColor: COLORS.error,
    borderRadius: 12,
    paddingVertical: SPACING.md,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  deleteButtonText: {
    ...TYPOGRAPHY.body,
    color: COLORS.card,
    fontWeight: '600',
    marginLeft: SPACING.xs,
  },
  revokeButton: {
    backgroundColor: COLORS.card,
    borderRadius: 12,
    paddingVertical: SPACING.md,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.secondary,
  },
  revokeButtonText: {
    ...TYPOGRAPHY.body,
    color: COLORS.secondary,
    fontWeight: '600',
    marginLeft: SPACING.xs,
  },
});
