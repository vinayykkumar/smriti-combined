import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
    View,
    Text,
    TextInput,
    StyleSheet,
    TouchableOpacity,
    FlatList,
    ActivityIndicator,
    Platform,
    ScrollView,
    Animated,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../styles/theme';
import { useDebounce } from '../hooks/useDebounce';
import { useToggle } from '../hooks/useToggle';
import { searchPosts } from '../services/api/posts';
import { STORAGE_KEY_SEARCH_HISTORY } from '../constants/config';
import PostCard from '../components/posts/PostCard';

const SERIF_FONT = Platform.OS === 'ios' ? 'Georgia' : 'serif';
const MAX_SEARCH_HISTORY = 10;
const PAGE_SIZE = 20;

const CONTENT_TYPES = [
    { label: 'All', value: null },
    { label: 'Note', value: 'note' },
    { label: 'Link', value: 'link' },
    { label: 'Image', value: 'image' },
    { label: 'Document', value: 'document' },
];

export default function SearchScreen({ navigation, route }) {
    // Search state
    const [searchText, setSearchText] = useState('');
    const [results, setResults] = useState([]);
    const [totalResults, setTotalResults] = useState(0);
    const [loading, setLoading] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);
    const [currentPage, setCurrentPage] = useState(0);
    const [hasSearched, setHasSearched] = useState(false);

    // Filter state
    const [filtersExpanded, toggleFilters, , collapseFilters] = useToggle(false);
    const [selectedContentType, setSelectedContentType] = useState(null);
    const [authorFilter, setAuthorFilter] = useState(null);
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    // Search history
    const [searchHistory, setSearchHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);

    // Animation for filters panel
    const filterHeight = useRef(new Animated.Value(0)).current;

    // Debounced search value
    const debouncedSearch = useDebounce(searchText, 500);

    // Handle initial params from navigation (e.g., author filter from profile)
    useEffect(() => {
        if (route?.params?.authorId && route?.params?.authorName) {
            setAuthorFilter({
                id: route.params.authorId,
                name: route.params.authorName
            });
        }
    }, [route?.params?.authorId, route?.params?.authorName]);

    // Load search history on mount
    useEffect(() => {
        loadSearchHistory();
    }, []);

    // Animate filters panel
    useEffect(() => {
        Animated.timing(filterHeight, {
            toValue: filtersExpanded ? 1 : 0,
            duration: 250,
            useNativeDriver: false,
        }).start();
    }, [filtersExpanded]);

    // Trigger search when debounced value changes
    useEffect(() => {
        if (debouncedSearch.trim() || authorFilter || selectedContentType || startDate || endDate) {
            performSearch(0);
        } else if (!debouncedSearch.trim() && !authorFilter && !selectedContentType && !startDate && !endDate) {
            setResults([]);
            setTotalResults(0);
            setHasSearched(false);
        }
    }, [debouncedSearch, authorFilter, selectedContentType, startDate, endDate]);

    const loadSearchHistory = async () => {
        try {
            const historyJson = await AsyncStorage.getItem(STORAGE_KEY_SEARCH_HISTORY);
            if (historyJson) {
                setSearchHistory(JSON.parse(historyJson));
            }
        } catch (error) {
            console.error('Error loading search history:', error);
        }
    };

    const saveSearchToHistory = async (query) => {
        if (!query.trim()) return;
        try {
            const updatedHistory = [
                query.trim(),
                ...searchHistory.filter(item => item !== query.trim())
            ].slice(0, MAX_SEARCH_HISTORY);

            setSearchHistory(updatedHistory);
            await AsyncStorage.setItem(STORAGE_KEY_SEARCH_HISTORY, JSON.stringify(updatedHistory));
        } catch (error) {
            console.error('Error saving search history:', error);
        }
    };

    const clearSearchHistory = async () => {
        try {
            setSearchHistory([]);
            await AsyncStorage.removeItem(STORAGE_KEY_SEARCH_HISTORY);
        } catch (error) {
            console.error('Error clearing search history:', error);
        }
    };

    const performSearch = useCallback(async (page = 0) => {
        const isNewSearch = page === 0;
        if (isNewSearch) {
            setLoading(true);
        } else {
            setLoadingMore(true);
        }

        try {
            const params = {
                skip: page * PAGE_SIZE,
                limit: PAGE_SIZE,
            };

            if (debouncedSearch.trim()) {
                params.q = debouncedSearch.trim();
            }
            if (authorFilter) {
                params.author_id = authorFilter.id;
            }
            if (selectedContentType) {
                params.content_type = selectedContentType;
            }
            if (startDate) {
                params.start_date = startDate;
            }
            if (endDate) {
                params.end_date = endDate;
            }

            const response = await searchPosts(params);

            if (response.success !== false && response.data) {
                const posts = response.data.posts || [];
                if (isNewSearch) {
                    setResults(posts);
                    // Save to history only on initial text search
                    if (debouncedSearch.trim()) {
                        saveSearchToHistory(debouncedSearch.trim());
                    }
                } else {
                    setResults(prev => [...prev, ...posts]);
                }
                setTotalResults(response.data.total || 0);
                setCurrentPage(page);
                setHasSearched(true);
            }
        } catch (error) {
            console.error('Search error:', error);
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    }, [debouncedSearch, authorFilter, selectedContentType, startDate, endDate]);

    const handleLoadMore = () => {
        if (!loadingMore && results.length < totalResults) {
            performSearch(currentPage + 1);
        }
    };

    const handleHistoryItemPress = (query) => {
        setSearchText(query);
        setShowHistory(false);
    };

    const handleAuthorPress = (authorUserId, authorUsername) => {
        navigation.navigate('UserProfile', {
            userId: authorUserId,
            username: authorUsername,
        });
    };

    const clearAuthorFilter = () => {
        setAuthorFilter(null);
    };

    const clearAllFilters = () => {
        setSelectedContentType(null);
        setAuthorFilter(null);
        setStartDate('');
        setEndDate('');
    };

    const hasActiveFilters = selectedContentType || authorFilter || startDate || endDate;

    const renderSearchInput = () => (
        <View style={styles.searchInputContainer}>
            <Ionicons name="search" size={20} color={COLORS.textLight} style={styles.searchIcon} />
            <TextInput
                style={styles.searchInput}
                placeholder="Search reflections..."
                placeholderTextColor={COLORS.textLight}
                value={searchText}
                onChangeText={(text) => {
                    setSearchText(text);
                    setShowHistory(text.length === 0);
                }}
                onFocus={() => {
                    if (!searchText) setShowHistory(true);
                }}
                onBlur={() => {
                    setTimeout(() => setShowHistory(false), 200);
                }}
                returnKeyType="search"
                autoCorrect={false}
            />
            {searchText.length > 0 && (
                <TouchableOpacity onPress={() => { setSearchText(''); setShowHistory(false); }}>
                    <Ionicons name="close-circle" size={20} color={COLORS.textLight} />
                </TouchableOpacity>
            )}
        </View>
    );

    const renderFilterToggle = () => (
        <TouchableOpacity style={styles.filterToggle} onPress={toggleFilters}>
            <Ionicons
                name={filtersExpanded ? 'options' : 'options-outline'}
                size={20}
                color={hasActiveFilters ? COLORS.primary : COLORS.textLight}
            />
            <Text style={[
                styles.filterToggleText,
                hasActiveFilters && styles.filterToggleTextActive
            ]}>
                Filters{hasActiveFilters ? ' (active)' : ''}
            </Text>
            <Ionicons
                name={filtersExpanded ? 'chevron-up' : 'chevron-down'}
                size={16}
                color={COLORS.textLight}
            />
        </TouchableOpacity>
    );

    const renderFiltersPanel = () => {
        const maxHeight = filterHeight.interpolate({
            inputRange: [0, 1],
            outputRange: [0, 300],
        });

        return (
            <Animated.View style={[styles.filtersPanel, { maxHeight, overflow: 'hidden' }]}>
                {/* Content type filter */}
                <Text style={styles.filterLabel}>Content Type</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipScrollView}>
                    {CONTENT_TYPES.map((type) => (
                        <TouchableOpacity
                            key={type.label}
                            style={[
                                styles.chip,
                                selectedContentType === type.value && styles.chipActive
                            ]}
                            onPress={() => setSelectedContentType(type.value)}
                        >
                            <Text style={[
                                styles.chipText,
                                selectedContentType === type.value && styles.chipTextActive
                            ]}>
                                {type.label}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>

                {/* Author filter display */}
                {authorFilter && (
                    <View style={styles.activeFilterRow}>
                        <Text style={styles.filterLabel}>Author</Text>
                        <View style={styles.authorFilterChip}>
                            <Text style={styles.authorFilterText}>@{authorFilter.name}</Text>
                            <TouchableOpacity onPress={clearAuthorFilter}>
                                <Ionicons name="close-circle" size={16} color={COLORS.secondary} />
                            </TouchableOpacity>
                        </View>
                    </View>
                )}

                {/* Date range filters */}
                <Text style={styles.filterLabel}>Date Range</Text>
                <View style={styles.dateRow}>
                    <View style={styles.dateInputWrapper}>
                        <TextInput
                            style={styles.dateInput}
                            placeholder="From (YYYY-MM-DD)"
                            placeholderTextColor={COLORS.textLight}
                            value={startDate}
                            onChangeText={setStartDate}
                            maxLength={10}
                        />
                    </View>
                    <Text style={styles.dateSeparator}>to</Text>
                    <View style={styles.dateInputWrapper}>
                        <TextInput
                            style={styles.dateInput}
                            placeholder="To (YYYY-MM-DD)"
                            placeholderTextColor={COLORS.textLight}
                            value={endDate}
                            onChangeText={setEndDate}
                            maxLength={10}
                        />
                    </View>
                </View>

                {/* Clear filters button */}
                {hasActiveFilters && (
                    <TouchableOpacity style={styles.clearFiltersButton} onPress={clearAllFilters}>
                        <Ionicons name="refresh-outline" size={16} color={COLORS.secondary} />
                        <Text style={styles.clearFiltersText}>Clear all filters</Text>
                    </TouchableOpacity>
                )}
            </Animated.View>
        );
    };

    const renderSearchHistory = () => {
        if (!showHistory || searchHistory.length === 0) return null;

        return (
            <View style={styles.historyContainer}>
                <View style={styles.historyHeader}>
                    <Text style={styles.historyTitle}>Recent Searches</Text>
                    <TouchableOpacity onPress={clearSearchHistory}>
                        <Text style={styles.historyClearText}>Clear</Text>
                    </TouchableOpacity>
                </View>
                {searchHistory.map((item, index) => (
                    <TouchableOpacity
                        key={`${item}-${index}`}
                        style={styles.historyItem}
                        onPress={() => handleHistoryItemPress(item)}
                    >
                        <Ionicons name="time-outline" size={16} color={COLORS.textLight} />
                        <Text style={styles.historyItemText} numberOfLines={1}>{item}</Text>
                    </TouchableOpacity>
                ))}
            </View>
        );
    };

    const renderPostItem = ({ item }) => (
        <PostCard post={item} onAuthorPress={handleAuthorPress} />
    );

    const renderEmpty = () => {
        if (loading) return null;
        if (!hasSearched) {
            return (
                <View style={styles.emptyState}>
                    <Ionicons name="search-outline" size={48} color={COLORS.textLight} />
                    <Text style={styles.emptyTitle}>Search Reflections</Text>
                    <Text style={styles.emptySubtitle}>
                        Find posts by text, author, date, or type
                    </Text>
                </View>
            );
        }
        return (
            <View style={styles.emptyState}>
                <Ionicons name="leaf-outline" size={48} color={COLORS.textLight} />
                <Text style={styles.emptyTitle}>No results found</Text>
                <Text style={styles.emptySubtitle}>
                    Try different search terms or adjust your filters
                </Text>
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

    const renderHeader = () => (
        <View>
            {renderSearchInput()}
            {renderFilterToggle()}
            {renderFiltersPanel()}
            {renderSearchHistory()}
            {hasSearched && !loading && (
                <View style={styles.resultsHeader}>
                    <Text style={styles.resultsCount}>
                        {totalResults} {totalResults === 1 ? 'result' : 'results'} found
                    </Text>
                </View>
            )}
        </View>
    );

    return (
        <View style={styles.container}>
            {/* Fixed Header */}
            <View style={styles.screenHeader}>
                <Text style={styles.headerTitle}>Search</Text>
            </View>

            {loading && !results.length ? (
                <View style={styles.loadingContainer}>
                    {renderHeader()}
                    <ActivityIndicator size="large" color={COLORS.accent} style={{ marginTop: 40 }} />
                </View>
            ) : (
                <FlatList
                    data={results}
                    renderItem={renderPostItem}
                    keyExtractor={(item) => item.postId || item._id || item.id || String(Math.random())}
                    ListHeaderComponent={renderHeader}
                    ListEmptyComponent={renderEmpty}
                    ListFooterComponent={renderFooter}
                    onEndReached={handleLoadMore}
                    onEndReachedThreshold={0.3}
                    contentContainerStyle={styles.listContent}
                    keyboardShouldPersistTaps="handled"
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
    screenHeader: {
        paddingTop: Platform.OS === 'ios' ? 60 : 40,
        paddingHorizontal: SPACING.lg,
        paddingBottom: SPACING.md,
        backgroundColor: COLORS.card,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.border,
        ...SHADOWS.small,
    },
    headerTitle: {
        ...TYPOGRAPHY.title,
        fontSize: 28,
        color: COLORS.primary,
        fontFamily: SERIF_FONT,
        fontWeight: '700',
    },
    listContent: {
        paddingBottom: 100,
    },
    loadingContainer: {
        flex: 1,
    },
    // Search Input
    searchInputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.card,
        marginHorizontal: SPACING.md,
        marginTop: SPACING.md,
        paddingHorizontal: SPACING.md,
        borderRadius: 16,
        borderWidth: 1,
        borderColor: COLORS.border,
        height: 48,
    },
    searchIcon: {
        marginRight: SPACING.sm,
    },
    searchInput: {
        flex: 1,
        fontSize: 16,
        color: COLORS.text,
        fontFamily: SERIF_FONT,
        paddingVertical: 0,
    },
    // Filters Toggle
    filterToggle: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: SPACING.lg,
        paddingVertical: SPACING.sm,
        marginTop: SPACING.xs,
    },
    filterToggleText: {
        fontSize: 14,
        color: COLORS.textLight,
        fontFamily: SERIF_FONT,
        marginHorizontal: SPACING.xs,
    },
    filterToggleTextActive: {
        color: COLORS.primary,
        fontWeight: '600',
    },
    // Filters Panel
    filtersPanel: {
        paddingHorizontal: SPACING.lg,
        paddingBottom: SPACING.sm,
    },
    filterLabel: {
        fontSize: 13,
        color: COLORS.textLight,
        fontFamily: SERIF_FONT,
        fontWeight: '600',
        marginTop: SPACING.sm,
        marginBottom: SPACING.xs,
        textTransform: 'uppercase',
        letterSpacing: 0.5,
    },
    chipScrollView: {
        flexDirection: 'row',
        marginBottom: SPACING.xs,
    },
    chip: {
        paddingHorizontal: SPACING.md,
        paddingVertical: 6,
        borderRadius: 20,
        backgroundColor: COLORS.card,
        borderWidth: 1,
        borderColor: COLORS.border,
        marginRight: SPACING.sm,
    },
    chipActive: {
        backgroundColor: COLORS.primary,
        borderColor: COLORS.primary,
    },
    chipText: {
        fontSize: 13,
        color: COLORS.textLight,
        fontFamily: SERIF_FONT,
    },
    chipTextActive: {
        color: COLORS.white,
    },
    activeFilterRow: {
        marginBottom: SPACING.xs,
    },
    authorFilterChip: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.card,
        alignSelf: 'flex-start',
        paddingHorizontal: SPACING.md,
        paddingVertical: 6,
        borderRadius: 20,
        borderWidth: 1,
        borderColor: COLORS.border,
        gap: SPACING.xs,
    },
    authorFilterText: {
        fontSize: 13,
        color: COLORS.secondary,
        fontFamily: SERIF_FONT,
        fontStyle: 'italic',
    },
    dateRow: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: SPACING.sm,
        marginBottom: SPACING.xs,
    },
    dateInputWrapper: {
        flex: 1,
    },
    dateInput: {
        backgroundColor: COLORS.card,
        borderWidth: 1,
        borderColor: COLORS.border,
        borderRadius: 10,
        paddingHorizontal: SPACING.sm,
        paddingVertical: 8,
        fontSize: 13,
        color: COLORS.text,
        fontFamily: SERIF_FONT,
    },
    dateSeparator: {
        fontSize: 13,
        color: COLORS.textLight,
        fontFamily: SERIF_FONT,
    },
    clearFiltersButton: {
        flexDirection: 'row',
        alignItems: 'center',
        alignSelf: 'flex-start',
        paddingVertical: SPACING.xs,
        gap: 4,
        marginTop: SPACING.xs,
    },
    clearFiltersText: {
        fontSize: 13,
        color: COLORS.secondary,
        fontFamily: SERIF_FONT,
    },
    // Search History
    historyContainer: {
        marginHorizontal: SPACING.md,
        marginTop: SPACING.sm,
        backgroundColor: COLORS.card,
        borderRadius: 12,
        padding: SPACING.md,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    historyHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: SPACING.sm,
    },
    historyTitle: {
        fontSize: 13,
        color: COLORS.textLight,
        fontFamily: SERIF_FONT,
        fontWeight: '600',
        textTransform: 'uppercase',
        letterSpacing: 0.5,
    },
    historyClearText: {
        fontSize: 13,
        color: COLORS.secondary,
        fontFamily: SERIF_FONT,
    },
    historyItem: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 8,
        gap: SPACING.sm,
    },
    historyItemText: {
        fontSize: 15,
        color: COLORS.text,
        fontFamily: SERIF_FONT,
        flex: 1,
    },
    // Results
    resultsHeader: {
        paddingHorizontal: SPACING.lg,
        paddingVertical: SPACING.sm,
    },
    resultsCount: {
        fontSize: 13,
        color: COLORS.textLight,
        fontFamily: SERIF_FONT,
        fontStyle: 'italic',
    },
    // Empty State
    emptyState: {
        alignItems: 'center',
        justifyContent: 'center',
        paddingTop: 80,
        paddingHorizontal: SPACING.xl,
    },
    emptyTitle: {
        fontSize: 18,
        color: COLORS.primary,
        fontFamily: SERIF_FONT,
        fontWeight: '600',
        marginTop: SPACING.md,
    },
    emptySubtitle: {
        fontSize: 14,
        color: COLORS.textLight,
        fontFamily: SERIF_FONT,
        textAlign: 'center',
        marginTop: SPACING.xs,
        lineHeight: 20,
    },
    // Load More
    loadMoreContainer: {
        paddingVertical: SPACING.lg,
        alignItems: 'center',
    },
});
