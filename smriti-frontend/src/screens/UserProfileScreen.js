import React, { useState, useEffect, useCallback } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ActivityIndicator,
    Platform,
    FlatList,
    RefreshControl,
    TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../styles/theme';
import { fetchUserProfileById, fetchUserPosts } from '../services/api/users';
import PostCard from '../components/posts/PostCard';

const SERIF_FONT = Platform.OS === 'ios' ? 'Georgia' : 'serif';
const PAGE_SIZE = 20;

export default function UserProfileScreen({ navigation, route }) {
    const { userId, username } = route.params;

    const [user, setUser] = useState(null);
    const [posts, setPosts] = useState([]);
    const [totalPosts, setTotalPosts] = useState(0);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);
    const [currentPage, setCurrentPage] = useState(0);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadProfile();
    }, [userId]);

    const loadProfile = async () => {
        setLoading(true);
        setError(null);
        try {
            const [profileResponse, postsResponse] = await Promise.all([
                fetchUserProfileById(userId),
                fetchUserPosts(userId, 0, PAGE_SIZE),
            ]);

            if (profileResponse.success !== false && profileResponse.data?.user) {
                setUser(profileResponse.data.user);
            } else {
                setError('User not found');
            }

            if (postsResponse.success !== false && postsResponse.data) {
                setPosts(postsResponse.data.posts || []);
                setTotalPosts(postsResponse.data.total || 0);
                setCurrentPage(0);
            }
        } catch (err) {
            setError('Failed to load profile');
            console.error('Profile load error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = async () => {
        setRefreshing(true);
        try {
            const [profileResponse, postsResponse] = await Promise.all([
                fetchUserProfileById(userId),
                fetchUserPosts(userId, 0, PAGE_SIZE),
            ]);

            if (profileResponse.success !== false && profileResponse.data?.user) {
                setUser(profileResponse.data.user);
            }
            if (postsResponse.success !== false && postsResponse.data) {
                setPosts(postsResponse.data.posts || []);
                setTotalPosts(postsResponse.data.total || 0);
                setCurrentPage(0);
            }
        } catch (err) {
            console.error('Refresh error:', err);
        } finally {
            setRefreshing(false);
        }
    };

    const handleLoadMore = async () => {
        if (loadingMore || posts.length >= totalPosts) return;

        setLoadingMore(true);
        try {
            const nextPage = currentPage + 1;
            const response = await fetchUserPosts(userId, nextPage * PAGE_SIZE, PAGE_SIZE);

            if (response.success !== false && response.data) {
                setPosts(prev => [...prev, ...(response.data.posts || [])]);
                setCurrentPage(nextPage);
            }
        } catch (err) {
            console.error('Load more error:', err);
        } finally {
            setLoadingMore(false);
        }
    };

    const handleAuthorPress = (authorUserId, authorUsername) => {
        if (authorUserId !== userId) {
            navigation.push('UserProfile', {
                userId: authorUserId,
                username: authorUsername,
            });
        }
    };

    const handleSearchByAuthor = () => {
        navigation.navigate('SearchTab', {
            screen: 'Search',
            params: {
                authorId: userId,
                authorName: user?.username || username,
            }
        });
    };

    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    };

    const renderHeader = () => {
        if (!user) return null;

        const initial = (user.username || username || '?').charAt(0).toUpperCase();
        const memberSince = formatDate(user.joined_at);

        return (
            <View style={styles.profileHeader}>
                {/* Avatar */}
                <View style={styles.avatarContainer}>
                    <View style={styles.avatar}>
                        <Text style={styles.avatarText}>{initial}</Text>
                    </View>
                </View>

                {/* Username */}
                <Text style={styles.username}>@{user.username}</Text>

                {/* Stats Row */}
                <View style={styles.statsRow}>
                    <View style={styles.statItem}>
                        <Text style={styles.statNumber}>{user.post_count || 0}</Text>
                        <Text style={styles.statLabel}>Reflections</Text>
                    </View>
                    <View style={styles.statDivider} />
                    <View style={styles.statItem}>
                        <Text style={styles.statNumber}>{memberSince}</Text>
                        <Text style={styles.statLabel}>Joined</Text>
                    </View>
                </View>

                {/* Filter by author button */}
                <TouchableOpacity style={styles.filterByAuthorButton} onPress={handleSearchByAuthor}>
                    <Ionicons name="search-outline" size={16} color={COLORS.secondary} />
                    <Text style={styles.filterByAuthorText}>Search posts by this author</Text>
                </TouchableOpacity>

                {/* Section header */}
                <View style={styles.sectionHeaderRow}>
                    <Text style={styles.sectionTitle}>Reflections</Text>
                    <View style={styles.sectionDivider} />
                </View>
            </View>
        );
    };

    const renderPostItem = ({ item }) => (
        <PostCard post={item} onAuthorPress={handleAuthorPress} />
    );

    const renderEmpty = () => {
        if (loading) return null;
        return (
            <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>No reflections yet.</Text>
            </View>
        );
    };

    const renderFooter = () => {
        if (loadingMore) {
            return (
                <View style={styles.loadMoreContainer}>
                    <ActivityIndicator size="small" color={COLORS.accent} />
                </View>
            );
        }
        return null;
    };

    if (loading) {
        return (
            <View style={styles.container}>
                <View style={styles.navBar}>
                    <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
                        <Ionicons name="arrow-back" size={24} color={COLORS.primary} />
                    </TouchableOpacity>
                    <Text style={styles.navTitle}>@{username}</Text>
                    <View style={{ width: 40 }} />
                </View>
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color={COLORS.accent} />
                </View>
            </View>
        );
    }

    if (error) {
        return (
            <View style={styles.container}>
                <View style={styles.navBar}>
                    <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
                        <Ionicons name="arrow-back" size={24} color={COLORS.primary} />
                    </TouchableOpacity>
                    <Text style={styles.navTitle}>Profile</Text>
                    <View style={{ width: 40 }} />
                </View>
                <View style={styles.errorContainer}>
                    <Ionicons name="alert-circle-outline" size={48} color={COLORS.textLight} />
                    <Text style={styles.errorText}>{error}</Text>
                    <TouchableOpacity style={styles.retryButton} onPress={loadProfile}>
                        <Text style={styles.retryText}>Retry</Text>
                    </TouchableOpacity>
                </View>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            {/* Navigation Bar */}
            <View style={styles.navBar}>
                <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
                    <Ionicons name="arrow-back" size={24} color={COLORS.primary} />
                </TouchableOpacity>
                <Text style={styles.navTitle}>@{user?.username || username}</Text>
                <View style={{ width: 40 }} />
            </View>

            <FlatList
                data={posts}
                renderItem={renderPostItem}
                keyExtractor={(item) => item.postId || item._id || item.id || String(Math.random())}
                ListHeaderComponent={renderHeader}
                ListEmptyComponent={renderEmpty}
                ListFooterComponent={renderFooter}
                onEndReached={handleLoadMore}
                onEndReachedThreshold={0.3}
                contentContainerStyle={styles.listContent}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={handleRefresh}
                        tintColor={COLORS.accent}
                    />
                }
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    navBar: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: Platform.OS === 'ios' ? 60 : 40,
        paddingHorizontal: SPACING.md,
        paddingBottom: SPACING.md,
        backgroundColor: COLORS.card,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.border,
        ...SHADOWS.small,
    },
    backButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        alignItems: 'center',
        justifyContent: 'center',
    },
    navTitle: {
        fontSize: 18,
        color: COLORS.primary,
        fontFamily: SERIF_FONT,
        fontWeight: '600',
    },
    loadingContainer: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
    },
    listContent: {
        paddingBottom: 100,
    },
    // Profile Header
    profileHeader: {
        alignItems: 'center',
        paddingTop: SPACING.xl,
        paddingBottom: SPACING.md,
    },
    avatarContainer: {
        marginBottom: SPACING.md,
        shadowColor: COLORS.shadow,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 10,
        elevation: 8,
    },
    avatar: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: COLORS.accent,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 3,
        borderColor: 'rgba(255,255,255,0.3)',
    },
    avatarText: {
        fontSize: 32,
        color: COLORS.white,
        fontFamily: SERIF_FONT,
    },
    username: {
        fontSize: 22,
        color: COLORS.primary,
        fontFamily: SERIF_FONT,
        marginBottom: SPACING.md,
    },
    statsRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: SPACING.md,
    },
    statItem: {
        alignItems: 'center',
        paddingHorizontal: SPACING.lg,
    },
    statNumber: {
        fontSize: 16,
        color: COLORS.primary,
        fontFamily: SERIF_FONT,
        fontWeight: '600',
    },
    statLabel: {
        fontSize: 12,
        color: COLORS.textLight,
        fontFamily: SERIF_FONT,
        marginTop: 2,
    },
    statDivider: {
        width: 1,
        height: 24,
        backgroundColor: COLORS.border,
    },
    filterByAuthorButton: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: SPACING.md,
        paddingVertical: 8,
        borderRadius: 20,
        borderWidth: 1,
        borderColor: COLORS.border,
        backgroundColor: COLORS.card,
        marginBottom: SPACING.lg,
        gap: 6,
    },
    filterByAuthorText: {
        fontSize: 13,
        color: COLORS.secondary,
        fontFamily: SERIF_FONT,
    },
    sectionHeaderRow: {
        flexDirection: 'row',
        alignItems: 'center',
        width: '100%',
        paddingHorizontal: SPACING.lg,
        gap: SPACING.md,
    },
    sectionTitle: {
        ...TYPOGRAPHY.heading,
        color: COLORS.secondary,
        fontSize: 18,
        fontWeight: '600',
        fontFamily: SERIF_FONT,
    },
    sectionDivider: {
        flex: 1,
        height: 1,
        backgroundColor: COLORS.border,
        opacity: 0.5,
    },
    // Empty
    emptyContainer: {
        padding: 40,
        alignItems: 'center',
    },
    emptyText: {
        fontSize: 16,
        color: COLORS.textLight,
        fontFamily: SERIF_FONT,
    },
    // Error
    errorContainer: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
        paddingHorizontal: SPACING.xl,
    },
    errorText: {
        fontSize: 16,
        color: COLORS.textLight,
        fontFamily: SERIF_FONT,
        marginTop: SPACING.md,
        textAlign: 'center',
    },
    retryButton: {
        marginTop: SPACING.md,
        paddingHorizontal: SPACING.lg,
        paddingVertical: SPACING.sm,
        borderRadius: 20,
        backgroundColor: COLORS.primary,
    },
    retryText: {
        fontSize: 14,
        color: COLORS.white,
        fontFamily: SERIF_FONT,
        fontWeight: '600',
    },
    // Load More
    loadMoreContainer: {
        paddingVertical: SPACING.lg,
        alignItems: 'center',
    },
});
