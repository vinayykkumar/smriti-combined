/**
 * CirclesListScreen
 * Displays the user's circles (Sangha) with ability to create/join
 */
import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../styles/theme';
import CircleCard from '../components/circles/CircleCard';
import CreateCircleModal from '../components/circles/CreateCircleModal';
import { useCircles } from '../hooks/useCircles';

export default function CirclesListScreen({ navigation }) {
  const {
    circles,
    loading,
    error,
    loadCircles,
    createCircle,
    joinCircle,
    refreshCircles
  } = useCircles();

  const [modalVisible, setModalVisible] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Load circles on mount and when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      loadCircles();
    }, [loadCircles])
  );

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshCircles();
    } finally {
      setRefreshing(false);
    }
  };

  const handleCirclePress = (circle) => {
    navigation.navigate('CircleDetail', {
      circleId: circle._id,
      circleName: circle.name
    });
  };

  const handleCreateCircle = async (data) => {
    const newCircle = await createCircle(data);
    if (newCircle) {
      // Navigate to the new circle
      navigation.navigate('CircleDetail', {
        circleId: newCircle._id,
        circleName: newCircle.name
      });
    }
  };

  const handleJoinCircle = async (inviteCode) => {
    const joinedCircle = await joinCircle(inviteCode);
    if (joinedCircle) {
      // Navigate to the joined circle
      navigation.navigate('CircleDetail', {
        circleId: joinedCircle._id,
        circleName: joinedCircle.name
      });
    }
  };

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="people-outline" size={64} color={COLORS.textLight} />
      <Text style={styles.emptyTitle}>No Circles Yet</Text>
      <Text style={styles.emptyText}>
        Create a circle to share reflections with your closest people,
        or join an existing one with an invite code.
      </Text>
      <TouchableOpacity
        style={styles.emptyButton}
        onPress={() => setModalVisible(true)}
      >
        <Ionicons name="add-circle" size={20} color={COLORS.card} />
        <Text style={styles.emptyButtonText}>Create Your First Circle</Text>
      </TouchableOpacity>
    </View>
  );

  const renderHeader = () => (
    <View style={styles.header}>
      <Text style={styles.headerTitle}>Your Circles</Text>
      <Text style={styles.headerSubtitle}>
        {circles.length} {circles.length === 1 ? 'circle' : 'circles'}
      </Text>
    </View>
  );

  if (loading && circles.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Loading circles...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={circles}
        keyExtractor={(item) => item._id}
        renderItem={({ item }) => (
          <CircleCard circle={item} onPress={handleCirclePress} />
        )}
        ListHeaderComponent={circles.length > 0 ? renderHeader : null}
        ListEmptyComponent={renderEmptyState}
        contentContainerStyle={[
          styles.listContent,
          circles.length === 0 && styles.listContentEmpty
        ]}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={COLORS.primary}
            colors={[COLORS.primary]}
          />
        }
        showsVerticalScrollIndicator={false}
      />

      {/* FAB - only show when there are existing circles */}
      {circles.length > 0 && (
        <TouchableOpacity
          style={styles.fab}
          onPress={() => setModalVisible(true)}
          activeOpacity={0.8}
        >
          <Ionicons name="add" size={28} color={COLORS.card} />
        </TouchableOpacity>
      )}

      {/* Create/Join Modal */}
      <CreateCircleModal
        visible={modalVisible}
        onClose={() => setModalVisible(false)}
        onCreateCircle={handleCreateCircle}
        onJoinCircle={handleJoinCircle}
        loading={loading}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textLight,
    marginTop: SPACING.md,
  },
  listContent: {
    paddingVertical: SPACING.md,
  },
  listContentEmpty: {
    flex: 1,
    justifyContent: 'center',
  },
  header: {
    paddingHorizontal: SPACING.lg,
    paddingBottom: SPACING.md,
  },
  headerTitle: {
    ...TYPOGRAPHY.heading,
    color: COLORS.text,
  },
  headerSubtitle: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginTop: 2,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: SPACING.xl,
  },
  emptyTitle: {
    ...TYPOGRAPHY.heading,
    color: COLORS.text,
    marginTop: SPACING.lg,
    marginBottom: SPACING.sm,
  },
  emptyText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textLight,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: SPACING.lg,
  },
  emptyButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 12,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.lg,
    flexDirection: 'row',
    alignItems: 'center',
    ...SHADOWS.small,
  },
  emptyButtonText: {
    ...TYPOGRAPHY.body,
    color: COLORS.card,
    fontWeight: '600',
    marginLeft: SPACING.sm,
  },
  fab: {
    position: 'absolute',
    bottom: SPACING.lg,
    right: SPACING.lg,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
    ...SHADOWS.medium,
  },
});
