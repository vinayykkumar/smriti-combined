import React, { useState, useEffect, useCallback } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    TouchableOpacity,
    ActivityIndicator,
    RefreshControl,
    Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, SHADOWS, TYPOGRAPHY } from '../styles/theme';
import { fetchQuoteHistory } from '../services/api/quotes';
import { useQuote } from '../hooks/useQuote';

/**
 * PastQuotesScreen - Displays history of received quotes
 *
 * Features:
 * - Paginated list of past quotes
 * - Pull to refresh
 * - Infinite scroll
 * - Tap to view full quote in popup
 *
 * Designed to feel like a quiet journal/history.
 */
export default function PastQuotesScreen({ navigation }) {
    const { openQuotePopup } = useQuote();

    // State
    const [quotes, setQuotes] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [error, setError] = useState(null);

    // Pagination
    const LIMIT = 20;

    // Fetch quotes
    const fetchQuotes = useCallback(async (skip = 0, append = false) => {
        try {
            const data = await fetchQuoteHistory(skip, LIMIT);

            if (append) {
                setQuotes(prev => [...prev, ...data.quotes]);
            } else {
                setQuotes(data.quotes);
            }

            setHasMore(data.has_more);
            setError(null);
        } catch (err) {
            console.error('Failed to fetch quote history:', err);
            setError(err.message || 'Failed to load quotes');
        }
    }, []);

    // Initial load
    useEffect(() => {
        const loadInitial = async () => {
            setIsLoading(true);
            await fetchQuotes(0, false);
            setIsLoading(false);
        };
        loadInitial();
    }, [fetchQuotes]);

    // Pull to refresh
    const handleRefresh = useCallback(async () => {
        setIsRefreshing(true);
        await fetchQuotes(0, false);
        setIsRefreshing(false);
    }, [fetchQuotes]);

    // Load more (infinite scroll)
    const handleLoadMore = useCallback(async () => {
        if (isLoadingMore || !hasMore) return;

        setIsLoadingMore(true);
        await fetchQuotes(quotes.length, true);
        setIsLoadingMore(false);
    }, [fetchQuotes, quotes.length, isLoadingMore, hasMore]);

    // Handle "View Full Post" - navigate to author's profile
    const handleViewPost = (quote) => {
        if (quote.author?.user_id) {
            navigation.navigate('UserProfile', {
                userId: quote.author.user_id,
                username: quote.author.username,
            });
        }
    };

    // Format date for display
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;

        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
        });
    };

    // Render individual quote item
    const renderQuoteItem = ({ item, index }) => (
        <View
            style={[
                styles.quoteCard,
                index === 0 && styles.firstCard,
            ]}
        >
            <Text style={styles.quoteText} numberOfLines={3}>
                "{item.text}"
            </Text>

            <View style={styles.quoteFooter}>
                {item.author?.username && (
                    <Text style={styles.authorText}>
                        — {item.author.username}
                    </Text>
                )}
                <Text style={styles.dateText}>
                    {formatDate(item.day_key)}
                </Text>
            </View>

            {item.author?.user_id && (
                <TouchableOpacity
                    style={styles.viewPostButton}
                    onPress={() => handleViewPost(item)}
                >
                    <Text style={styles.viewPostText}>View Full Post</Text>
                </TouchableOpacity>
            )}
        </View>
    );

    // Render empty state
    const renderEmptyState = () => (
        <View style={styles.emptyContainer}>
            <Ionicons
                name="book-outline"
                size={64}
                color={COLORS.border}
            />
            <Text style={styles.emptyTitle}>No quotes yet</Text>
            <Text style={styles.emptySubtitle}>
                Your daily quotes will appear here
            </Text>
        </View>
    );

    // Render footer (loading indicator)
    const renderFooter = () => {
        if (!isLoadingMore) return null;
        return (
            <View style={styles.footerLoader}>
                <ActivityIndicator size="small" color={COLORS.textLight} />
            </View>
        );
    };

    // Render error state
    if (error && quotes.length === 0) {
        return (
            <View style={styles.container}>
                <View style={styles.header}>
                    <TouchableOpacity
                        style={styles.backButton}
                        onPress={() => navigation.goBack()}
                    >
                        <Ionicons name="arrow-back" size={24} color={COLORS.text} />
                    </TouchableOpacity>
                    <Text style={styles.headerTitle}>Past Quotes</Text>
                    <View style={styles.headerSpacer} />
                </View>

                <View style={styles.errorContainer}>
                    <Ionicons name="alert-circle-outline" size={48} color={COLORS.error} />
                    <Text style={styles.errorText}>{error}</Text>
                    <TouchableOpacity
                        style={styles.retryButton}
                        onPress={() => {
                            setIsLoading(true);
                            setError(null);
                            fetchQuotes(0, false).finally(() => setIsLoading(false));
                        }}
                    >
                        <Text style={styles.retryText}>Try Again</Text>
                    </TouchableOpacity>
                </View>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <TouchableOpacity
                    style={styles.backButton}
                    onPress={() => navigation.goBack()}
                >
                    <Ionicons name="arrow-back" size={24} color={COLORS.text} />
                </TouchableOpacity>
                <Text style={styles.headerTitle}>Past Quotes</Text>
                <View style={styles.headerSpacer} />
            </View>

            {/* Loading state */}
            {isLoading ? (
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color={COLORS.secondary} />
                </View>
            ) : (
                <FlatList
                    data={quotes}
                    renderItem={renderQuoteItem}
                    keyExtractor={(item, index) => `${item.day_key}-${index}`}
                    contentContainerStyle={[
                        styles.listContent,
                        quotes.length === 0 && styles.emptyListContent,
                    ]}
                    refreshControl={
                        <RefreshControl
                            refreshing={isRefreshing}
                            onRefresh={handleRefresh}
                            tintColor={COLORS.secondary}
                            colors={[COLORS.secondary]}
                        />
                    }
                    onEndReached={handleLoadMore}
                    onEndReachedThreshold={0.3}
                    ListEmptyComponent={renderEmptyState}
                    ListFooterComponent={renderFooter}
                    showsVerticalScrollIndicator={false}
                />
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: Platform.OS === 'ios' ? 60 : 40,
        paddingHorizontal: SPACING.lg,
        paddingBottom: SPACING.md,
        backgroundColor: COLORS.background,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.border,
    },
    backButton: {
        padding: SPACING.xs,
    },
    headerTitle: {
        ...TYPOGRAPHY.heading,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.text,
    },
    headerSpacer: {
        width: 32, // Match back button width for centering
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    listContent: {
        padding: SPACING.md,
        paddingBottom: SPACING.xxl,
    },
    emptyListContent: {
        flex: 1,
    },
    quoteCard: {
        backgroundColor: COLORS.card,
        borderRadius: 16,
        padding: SPACING.lg,
        marginBottom: SPACING.md,
        ...SHADOWS.small,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    firstCard: {
        marginTop: SPACING.sm,
    },
    quoteText: {
        fontSize: 16,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.text,
        lineHeight: 26,
        marginBottom: SPACING.md,
    },
    quoteFooter: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: SPACING.sm,
        borderTopWidth: 1,
        borderTopColor: COLORS.border,
    },
    authorText: {
        fontSize: 13,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        fontStyle: 'italic',
        color: COLORS.textLight,
    },
    dateText: {
        fontSize: 12,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.textLight,
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: SPACING.xl,
    },
    emptyTitle: {
        fontSize: 20,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.text,
        marginTop: SPACING.lg,
        marginBottom: SPACING.sm,
    },
    emptySubtitle: {
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.textLight,
        textAlign: 'center',
    },
    footerLoader: {
        paddingVertical: SPACING.lg,
        alignItems: 'center',
    },
    errorContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: SPACING.xl,
    },
    errorText: {
        fontSize: 16,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.error,
        textAlign: 'center',
        marginTop: SPACING.md,
        marginBottom: SPACING.lg,
    },
    retryButton: {
        paddingVertical: SPACING.sm,
        paddingHorizontal: SPACING.lg,
        backgroundColor: COLORS.secondary,
        borderRadius: 20,
    },
    retryText: {
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.white,
    },
    viewPostButton: {
        marginTop: SPACING.sm,
        paddingTop: SPACING.sm,
        alignItems: 'flex-end',
    },
    viewPostText: {
        fontSize: 13,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.secondary,
        textDecorationLine: 'underline',
    },
});
