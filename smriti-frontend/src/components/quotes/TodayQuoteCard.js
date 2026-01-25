import React, { useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    Platform,
    ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, SHADOWS } from '../../styles/theme';
import { useQuote } from '../../hooks/useQuote';

/**
 * TodayQuoteCard - Displays today's quote preview on the HomeScreen
 *
 * States:
 * - delivered: Shows quote preview with "Tap to read"
 * - pending: Shows "Your quote will arrive today"
 * - unavailable: Hidden (returns null)
 * - loading: Shows subtle loading indicator
 *
 * Designed to be calm and minimal.
 */
export default function TodayQuoteCard({ navigation }) {
    const {
        todayQuote,
        isLoading,
        openQuotePopup,
        refreshTodayQuote,
    } = useQuote();

    // Fetch quote on mount if we don't have it
    useEffect(() => {
        if (!todayQuote) {
            refreshTodayQuote();
        }
    }, []);

    // Handle card tap
    const handlePress = () => {
        openQuotePopup();
    };

    // Handle "Past Quotes" link
    const handlePastQuotes = () => {
        if (navigation) {
            navigation.navigate('PastQuotes');
        }
    };

    // Don't render if unavailable
    if (todayQuote?.status === 'unavailable') {
        return null;
    }

    // Loading state - show minimal placeholder
    if (isLoading && !todayQuote) {
        return (
            <View style={styles.container}>
                <View style={styles.card}>
                    <View style={styles.loadingContent}>
                        <ActivityIndicator size="small" color={COLORS.textLight} />
                    </View>
                </View>
            </View>
        );
    }

    // Pending state - quote will arrive later
    if (todayQuote?.status === 'pending') {
        return (
            <View style={styles.container}>
                <TouchableOpacity
                    style={styles.card}
                    onPress={handlePress}
                    activeOpacity={0.8}
                >
                    <View style={styles.headerRow}>
                        <Ionicons
                            name="sparkles-outline"
                            size={16}
                            color={COLORS.textLight}
                        />
                        <Text style={styles.headerText}>Today's Quote</Text>
                    </View>

                    <View style={styles.pendingContent}>
                        <Text style={styles.pendingText}>
                            Your quote will arrive today
                        </Text>
                        <Text style={styles.hintText}>
                            We'll notify you when it's ready
                        </Text>
                    </View>

                    <View style={styles.footer}>
                        <TouchableOpacity onPress={handlePastQuotes}>
                            <Text style={styles.pastQuotesLink}>
                                Past Quotes <Ionicons name="chevron-forward" size={12} />
                            </Text>
                        </TouchableOpacity>
                    </View>
                </TouchableOpacity>
            </View>
        );
    }

    // Delivered state - show quote preview
    if (todayQuote?.status === 'delivered' && todayQuote?.quote) {
        const quote = todayQuote.quote;
        // Truncate quote for preview (max ~80 chars)
        const previewText = quote.text.length > 80
            ? quote.text.substring(0, 77) + '...'
            : quote.text;

        return (
            <View style={styles.container}>
                <TouchableOpacity
                    style={styles.card}
                    onPress={handlePress}
                    activeOpacity={0.8}
                >
                    <View style={styles.headerRow}>
                        <Ionicons
                            name="sparkles"
                            size={16}
                            color={COLORS.secondary}
                        />
                        <Text style={styles.headerText}>Today's Quote</Text>
                    </View>

                    <Text style={styles.quotePreview}>"{previewText}"</Text>

                    <Text style={styles.tapHint}>Tap to read</Text>

                    <View style={styles.footer}>
                        <TouchableOpacity onPress={handlePastQuotes}>
                            <Text style={styles.pastQuotesLink}>
                                Past Quotes <Ionicons name="chevron-forward" size={12} />
                            </Text>
                        </TouchableOpacity>
                    </View>
                </TouchableOpacity>
            </View>
        );
    }

    // Default - nothing to show yet
    return null;
}

const styles = StyleSheet.create({
    container: {
        paddingHorizontal: SPACING.md,
        paddingBottom: SPACING.lg,
    },
    card: {
        backgroundColor: COLORS.card,
        borderRadius: 16,
        padding: SPACING.lg,
        ...SHADOWS.small,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    headerRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: SPACING.md,
    },
    headerText: {
        fontSize: 12,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.textLight,
        marginLeft: SPACING.xs,
        letterSpacing: 0.5,
        textTransform: 'uppercase',
    },
    loadingContent: {
        paddingVertical: SPACING.lg,
        alignItems: 'center',
    },
    pendingContent: {
        alignItems: 'center',
        paddingVertical: SPACING.sm,
    },
    pendingText: {
        fontSize: 16,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.text,
        textAlign: 'center',
        marginBottom: SPACING.xs,
    },
    hintText: {
        fontSize: 13,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.textLight,
        fontStyle: 'italic',
    },
    quotePreview: {
        fontSize: 16,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.text,
        lineHeight: 24,
        textAlign: 'center',
        marginBottom: SPACING.sm,
    },
    tapHint: {
        fontSize: 12,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.textLight,
        fontStyle: 'italic',
        textAlign: 'center',
        marginBottom: SPACING.sm,
    },
    footer: {
        flexDirection: 'row',
        justifyContent: 'flex-end',
        marginTop: SPACING.sm,
        paddingTop: SPACING.sm,
        borderTopWidth: 1,
        borderTopColor: COLORS.border,
    },
    pastQuotesLink: {
        fontSize: 13,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.secondary,
    },
});
