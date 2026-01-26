/**
 * CircleFeedScreen
 * Main feed view for a specific circle - like HomeScreen but circle-specific
 * Shows posts shared to this circle with "Post to Circle" FAB
 */
import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../styles/theme';
import CircleHeader from '../components/circles/CircleHeader';
import PostCard from '../components/posts/PostCard';
import * as circlesApi from '../services/api/circles';

export default function CircleFeedScreen({ route, navigation }) {
  const { circleId, circleName } = route.params;

  const [circle, setCircle] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);

  const POSTS_PER_PAGE = 20;

  // Load circle details
  const loadCircleDetails = useCallback(async () => {
    try {
      const data = await circlesApi.getCircleDetails(circleId);
      setCircle(data);
    } catch (err) {
      console.error('Failed to load circle:', err);
    }
  }, [circleId]);

  // Load posts with pagination
  const loadPosts = useCallback(async (skip = 0, append = false) => {
    try {
      const { posts: newPosts, total: totalCount } = await circlesApi.getCirclePosts(
        circleId,
        skip,
        POSTS_PER_PAGE
      );

      if (append) {
        setPosts(prev => [...prev, ...newPosts]);
      } else {
        setPosts(newPosts);
      }

      setTotal(totalCount);
      setHasMore(skip + newPosts.length < totalCount);
    } catch (err) {
      console.error('Failed to load posts:', err);
      if (!append) {
        Alert.alert('Error', 'Failed to load circle posts');
      }
    }
  }, [circleId]);

  // Initial load
  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([loadCircleDetails(), loadPosts(0, false)]);
    } finally {
      setLoading(false);
    }
  }, [loadCircleDetails, loadPosts]);

  // Load on focus
  useFocusEffect(
    useCallback(() => {
      loadAll();
    }, [loadAll])
  );

  // Update header title
  useEffect(() => {
    navigation.setOptions({
      headerTitle: circleName || 'Circle',
    });
  }, [navigation, circleName]);

  // Pull to refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await Promise.all([loadCircleDetails(), loadPosts(0, false)]);
    } finally {
      setRefreshing(false);
    }
  };

  // Load more (infinite scroll)
  const handleLoadMore = async () => {
    if (loadingMore || !hasMore) return;

    setLoadingMore(true);
    try {
      await loadPosts(posts.length, true);
    } finally {
      setLoadingMore(false);
    }
  };

  // Navigate to settings
  const handleSettingsPress = () => {
    navigation.navigate('CircleSettings', {
      circleId,
      circleName: circle?.name || circleName,
    });
  };

  // Navigate to members list
  const handleMembersPress = () => {
    navigation.navigate('CircleSettings', {
      circleId,
      circleName: circle?.name || circleName,
      initialTab: 'members',
    });
  };

  // Create new post in this circle
  const handleCreatePost = () => {
    navigation.navigate('CreateCirclePost', {
      circleId,
      circleName: circle?.name || circleName,
    });
  };

  // View user profile
  const handleAuthorPress = (userId) => {
    navigation.navigate('UserProfile', { userId });
  };

  // Render empty state
  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="chatbubbles-outline" size={64} color={COLORS.textLight} />
      <Text style={styles.emptyTitle}>No Reflections Yet</Text>
      <Text style={styles.emptyText}>
        Be the first to share a reflection with this circle.
        Your thoughts are safe here.
      </Text>
      <TouchableOpacity style={styles.emptyButton} onPress={handleCreatePost}>
        <Ionicons name="add" size={20} color={COLORS.card} />
        <Text style={styles.emptyButtonText}>Share a Reflection</Text>
      </TouchableOpacity>
    </View>
  );

  // Render footer (loading more indicator)
  const renderFooter = () => {
    if (!loadingMore) return null;
    return (
      <View style={styles.footerLoader}>
        <ActivityIndicator size="small" color={COLORS.primary} />
      </View>
    );
  };

  // Loading state
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Loading circle...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={posts}
        keyExtractor={(item) => item._id}
        renderItem={({ item }) => (
          <PostCard
            post={item}
            onAuthorPress={handleAuthorPress}
          />
        )}
        ListHeaderComponent={
          <CircleHeader
            circle={circle}
            onSettingsPress={handleSettingsPress}
            onMembersPress={handleMembersPress}
          />
        }
        ListEmptyComponent={renderEmptyState}
        ListFooterComponent={renderFooter}
        contentContainerStyle={[
          styles.listContent,
          posts.length === 0 && styles.listContentEmpty,
        ]}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={COLORS.primary}
            colors={[COLORS.primary]}
          />
        }
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.3}
        showsVerticalScrollIndicator={false}
      />

      {/* FAB - Post to Circle */}
      <TouchableOpacity
        style={styles.fab}
        onPress={handleCreatePost}
        activeOpacity={0.8}
      >
        <Ionicons name="create" size={24} color={COLORS.card} />
        <Text style={styles.fabText}>Post</Text>
      </TouchableOpacity>
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
    paddingBottom: 100, // Space for FAB
  },
  listContentEmpty: {
    flex: 1,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: SPACING.xl,
    paddingTop: SPACING.xxl,
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
  footerLoader: {
    paddingVertical: SPACING.lg,
    alignItems: 'center',
  },
  fab: {
    position: 'absolute',
    bottom: SPACING.lg,
    right: SPACING.lg,
    backgroundColor: COLORS.primary,
    borderRadius: 28,
    paddingVertical: SPACING.sm + 2,
    paddingHorizontal: SPACING.md,
    flexDirection: 'row',
    alignItems: 'center',
    ...SHADOWS.medium,
  },
  fabText: {
    ...TYPOGRAPHY.body,
    color: COLORS.card,
    fontWeight: '600',
    marginLeft: SPACING.xs,
  },
});
