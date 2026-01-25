import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    Modal,
    TouchableOpacity,
    TouchableWithoutFeedback,
    ActivityIndicator,
    Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { COLORS, SPACING, SHADOWS } from '../../styles/theme';
import { useQuote } from '../../hooks/useQuote';

/**
 * QuotePopup - Modal that displays today's quote
 *
 * Shows:
 * - Quote text (large, centered)
 * - Author attribution
 * - "View Full Post" button
 *
 * Designed to feel calm and minimal, not like an ad.
 */
export default function QuotePopup() {
    const navigation = useNavigation();
    const {
        isQuotePopupOpen,
        closeQuotePopup,
        todayQuote,
        isLoading,
        error,
    } = useQuote();

    // Handle navigation to full post (navigate to author's profile)
    const handleViewPost = () => {
        if (todayQuote?.quote?.author?.user_id) {
            closeQuotePopup();
            navigation.navigate('UserProfile', {
                userId: todayQuote.quote.author.user_id,
                username: todayQuote.quote.author.username,
            });
        }
    };

    // Handle viewing author profile
    const handleViewAuthor = () => {
        if (todayQuote?.quote?.author?.user_id) {
            closeQuotePopup();
            navigation.navigate('UserProfile', {
                userId: todayQuote.quote.author.user_id,
                username: todayQuote.quote.author.username,
            });
        }
    };

    // Handle navigation to Past Quotes
    const handlePastQuotes = () => {
        closeQuotePopup();
        navigation.navigate('PastQuotes');
    };

    // Render content based on state
    const renderContent = () => {
        if (isLoading) {
            return (
                <View style={styles.centerContent}>
                    <ActivityIndicator size="large" color={COLORS.secondary} />
                    <Text style={styles.loadingText}>Loading your quote...</Text>
                </View>
            );
        }

        if (error) {
            return (
                <View style={styles.centerContent}>
                    <Text style={styles.errorText}>Could not load quote</Text>
                    <Text style={styles.subtleText}>Please try again later</Text>
                </View>
            );
        }

        if (!todayQuote) {
            return (
                <View style={styles.centerContent}>
                    <Text style={styles.subtleText}>Loading...</Text>
                </View>
            );
        }

        // Quote pending - will arrive later
        if (todayQuote.status === 'pending') {
            return (
                <View style={styles.centerContent}>
                    <Ionicons
                        name="time-outline"
                        size={48}
                        color={COLORS.textLight}
                        style={styles.pendingIcon}
                    />
                    <Text style={styles.pendingText}>
                        Your quote will arrive{'\n'}later today
                    </Text>
                    <Text style={styles.subtleText}>
                        Check back soon
                    </Text>
                </View>
            );
        }

        // No quote available today
        if (todayQuote.status === 'unavailable') {
            return (
                <View style={styles.centerContent}>
                    <Text style={styles.pendingText}>
                        No quote available today
                    </Text>
                    <Text style={styles.subtleText}>
                        {todayQuote.message || 'Check back tomorrow'}
                    </Text>
                </View>
            );
        }

        // Quote delivered - show it
        const quote = todayQuote.quote;
        return (
            <View style={styles.quoteContent}>
                <Text style={styles.quoteText}>"{quote.text}"</Text>

                {quote.author?.username && (
                    <TouchableOpacity
                        onPress={handleViewAuthor}
                        style={styles.authorContainer}
                    >
                        <Text style={styles.authorText}>
                            — {quote.author.username}
                        </Text>
                    </TouchableOpacity>
                )}

                {quote.post_id && (
                    <TouchableOpacity
                        onPress={handleViewPost}
                        style={styles.viewPostButton}
                    >
                        <Text style={styles.viewPostText}>View Full Post</Text>
                    </TouchableOpacity>
                )}
            </View>
        );
    };

    return (
        <Modal
            visible={isQuotePopupOpen}
            transparent={true}
            animationType="fade"
            onRequestClose={closeQuotePopup}
        >
            <TouchableWithoutFeedback onPress={closeQuotePopup}>
                <View style={styles.overlay}>
                    <TouchableWithoutFeedback onPress={() => { }}>
                        <View style={styles.popup}>
                            {/* Close button */}
                            <TouchableOpacity
                                style={styles.closeButton}
                                onPress={closeQuotePopup}
                                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                            >
                                <Ionicons
                                    name="close"
                                    size={24}
                                    color={COLORS.textLight}
                                />
                            </TouchableOpacity>

                            {/* Header */}
                            <Text style={styles.header}>Today's Quote</Text>

                            {/* Content */}
                            {renderContent()}

                            {/* Footer with Past Quotes link */}
                            <View style={styles.footer}>
                                <TouchableOpacity onPress={handlePastQuotes}>
                                    <Text style={styles.pastQuotesLink}>
                                        Past Quotes <Ionicons name="chevron-forward" size={12} />
                                    </Text>
                                </TouchableOpacity>
                            </View>
                        </View>
                    </TouchableWithoutFeedback>
                </View>
            </TouchableWithoutFeedback>
        </Modal>
    );
}

const styles = StyleSheet.create({
    overlay: {
        flex: 1,
        backgroundColor: 'rgba(0, 0, 0, 0.4)',
        justifyContent: 'center',
        alignItems: 'center',
        padding: SPACING.lg,
    },
    popup: {
        backgroundColor: COLORS.card,
        borderRadius: 24,
        padding: SPACING.xl,
        paddingTop: SPACING.lg,
        width: '100%',
        maxWidth: 340,
        minHeight: 280,
        ...SHADOWS.medium,
    },
    closeButton: {
        position: 'absolute',
        top: SPACING.md,
        right: SPACING.md,
        zIndex: 10,
        padding: SPACING.xs,
    },
    header: {
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.textLight,
        textAlign: 'center',
        marginBottom: SPACING.lg,
        letterSpacing: 1,
        textTransform: 'uppercase',
    },
    centerContent: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingVertical: SPACING.xl,
    },
    quoteContent: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    quoteText: {
        fontSize: 20,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.text,
        textAlign: 'center',
        lineHeight: 32,
        marginBottom: SPACING.lg,
    },
    authorContainer: {
        marginBottom: SPACING.lg,
    },
    authorText: {
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        fontStyle: 'italic',
        color: COLORS.textLight,
        textAlign: 'center',
    },
    viewPostButton: {
        paddingVertical: SPACING.sm,
        paddingHorizontal: SPACING.md,
    },
    viewPostText: {
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.secondary,
        textDecorationLine: 'underline',
    },
    loadingText: {
        marginTop: SPACING.md,
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.textLight,
    },
    errorText: {
        fontSize: 16,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.error,
        marginBottom: SPACING.sm,
    },
    pendingIcon: {
        marginBottom: SPACING.md,
        opacity: 0.6,
    },
    pendingText: {
        fontSize: 18,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.text,
        textAlign: 'center',
        lineHeight: 28,
        marginBottom: SPACING.sm,
    },
    subtleText: {
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.textLight,
        textAlign: 'center',
    },
    footer: {
        marginTop: SPACING.lg,
        paddingTop: SPACING.md,
        borderTopWidth: 1,
        borderTopColor: COLORS.border,
        alignItems: 'center',
    },
    pastQuotesLink: {
        fontSize: 13,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        color: COLORS.secondary,
    },
});
