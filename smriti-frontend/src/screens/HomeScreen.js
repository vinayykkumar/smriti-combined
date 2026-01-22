import React, { useState, useEffect, useRef } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Image,
    TouchableOpacity,
    Linking,
    AppState,
    Platform,
    ImageBackground
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../styles/theme';
import { usePosts } from '../hooks/usePosts';
import { PostList } from '../components';

export default function HomeScreen({ onCreatePost }) {
    const { posts, refreshing, refreshPosts } = usePosts();
    const appState = useRef(AppState.currentState);

    // Auto-refresh when app comes to foreground
    useEffect(() => {
        const subscription = AppState.addEventListener('change', nextAppState => {
            if (
                appState.current.match(/inactive|background/) &&
                nextAppState === 'active'
            ) {
                console.log('App has come to the foreground! Refreshing posts...');
                refreshPosts();
            }

            appState.current = nextAppState;
        });

        return () => {
            subscription.remove();
        };
    }, [refreshPosts]);

    // Static data for the featured card
    const cardData = {
        title: '🌱 Why Smriti exists?',
        description: 'Smriti is a quiet digital space to pause, reflect, and remember. There are no likes, comments, or noise here.\n\nOnly sincere learnings, gentle reminders, and shared reflections.',
        imageUri: require('../../assets/daily_inspiration.png'),
        author: 'Reflections',
        links: []
    };

    const handleLinkPress = async (url) => {
        const supported = await Linking.canOpenURL(url);
        if (supported) {
            await Linking.openURL(url);
        } else {
            console.error(`Don't know how to open this URL: ${url}`);
        }
    };

    const renderScrollableHeader = () => (
        <View>
            <View style={styles.sectionContainer}>
                <ImageBackground
                    source={require('../../assets/bg_card.jpg')}
                    style={styles.card}
                    resizeMode="cover"
                    imageStyle={{ borderRadius: 20 }}
                >
                    <View style={styles.cardImageContainer}>
                        <Image
                            source={cardData.imageUri}
                            style={styles.cardImage}
                            resizeMode="cover"
                        />
                        <View style={styles.cardOverlay} />
                    </View>

                    <View style={styles.cardContent}>
                        <Text style={styles.cardTitle}>{cardData.title}</Text>

                        {cardData.author && (
                            <View style={styles.authorContainer}>
                                <Text style={styles.authorText}>{cardData.author}</Text>
                            </View>
                        )}

                        <Text style={styles.cardText}>{cardData.description}</Text>
                    </View>
                </ImageBackground>
            </View>

            {posts.length > 0 && (
                <View style={styles.feedHeader}>
                    <Text style={styles.sectionTitle}>Reflections</Text>
                    <View style={styles.sectionDivider} />
                </View>
            )}
        </View>
    );

    return (
        <ImageBackground
            source={require('../../assets/bg_home_page.jpg')}
            style={styles.container}
            resizeMode="cover"
        >
            {/* Fixed Header */}
            <ImageBackground
                source={require('../../assets/bg_home_page.jpg')}
                style={styles.fixedHeader}
                resizeMode="cover"
                imageStyle={{ borderBottomLeftRadius: 24, borderBottomRightRadius: 24 }}
            >
                {/* Overlay to modify background tone */}
                <View style={[StyleSheet.absoluteFill, {
                    backgroundColor: 'rgba(141, 110, 99, 0.1)', // Light brown tint 
                    borderBottomLeftRadius: 24,
                    borderBottomRightRadius: 24,
                }]} />

                <View style={styles.headerTopRow}>
                    <View style={styles.headerTextContainer}>
                        <Text style={styles.headerTitle}>Hari Om</Text>
                        <Text style={styles.headerSubtitle}>Daily Reflections</Text>
                    </View>
                </View>
            </ImageBackground>

            <PostList
                posts={posts}
                onRefresh={refreshPosts}
                refreshing={refreshing}
                ListHeaderComponent={renderScrollableHeader}
                contentContainerStyle={styles.scrollContent}
            />

            {/* FAB (Floating Action Button) */}
            <TouchableOpacity style={styles.fab} onPress={onCreatePost}>
                <Text style={styles.fabText}>+</Text>
            </TouchableOpacity>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        // backgroundColor: COLORS.background, // Handled by ImageBackground
        // paddingTop: 50, // Removed, handled by Fixed Header padding
    },
    fixedHeader: {
        paddingTop: Platform.OS === 'ios' ? 60 : 40, // Handle status bar here since it's an ImageBackground now
        paddingHorizontal: SPACING.lg,
        paddingBottom: SPACING.lg,
        zIndex: 10,
        ...SHADOWS.medium, // Add shadow for depth
        shadowColor: COLORS.shadow,
        shadowOpacity: 0.15,
    },
    headerTopRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    headerTextContainer: {
        flex: 1,
    },
    headerIconContainer: {
        width: 44,
        height: 44,
        borderRadius: 22,
        backgroundColor: 'rgba(255,255,255,0.3)', // Subtle highlight behind icon
        justifyContent: 'center',
        alignItems: 'center',
    },
    headerTitle: {
        ...TYPOGRAPHY.title,
        color: COLORS.primary,
        fontSize: 32,
        fontWeight: '700',
        letterSpacing: -0.5,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    },
    headerSubtitle: {
        ...TYPOGRAPHY.body,
        color: COLORS.secondary,
        fontSize: 16,
        marginTop: -4,
        letterSpacing: 0.5,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        fontStyle: 'italic',
    },
    scrollContent: {
        paddingBottom: 80, // Space for FAB
    },
    sectionContainer: {
        paddingHorizontal: SPACING.md,
        paddingBottom: SPACING.lg,
    },
    feedHeader: {
        paddingHorizontal: SPACING.lg,
        marginBottom: SPACING.sm,
        flexDirection: 'row',
        alignItems: 'center',
        gap: SPACING.md,
    },
    sectionTitle: {
        ...TYPOGRAPHY.heading,
        color: COLORS.secondary,
        fontSize: 20,
        fontWeight: '600',
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
    },
    sectionDivider: {
        flex: 1,
        height: 1,
        backgroundColor: COLORS.border,
        opacity: 0.5,
    },
    card: {
        backgroundColor: COLORS.card,
        borderRadius: 20,
        ...SHADOWS.medium,
        shadowColor: COLORS.shadow,
        shadowOpacity: 0.1,
        overflow: 'hidden',
        borderWidth: 1.5,
        borderColor: 'rgba(78, 52, 46, 0.2)', // Increased visibility
    },
    cardImageContainer: {
        position: 'relative',
        height: 220,
    },
    cardImage: {
        width: '100%',
        height: '100%',
        backgroundColor: COLORS.border,
    },
    cardOverlay: {
        ...StyleSheet.absoluteFillObject,
        backgroundColor: 'rgba(0,0,0,0.02)', // Subtle tint
    },
    cardContent: {
        padding: SPACING.lg,
        paddingTop: SPACING.md, // Reduced slightly
        alignItems: 'center', // Center everything in content
    },
    cardTitle: {
        ...TYPOGRAPHY.heading,
        fontSize: 24,
        marginBottom: SPACING.xs,
        color: COLORS.primary,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        fontWeight: '700',
        textAlign: 'center',
    },
    cardText: {
        ...TYPOGRAPHY.body,
        color: COLORS.text,
        lineHeight: 28, // Increased for center alignment readability
        fontSize: 16,
        opacity: 0.9,
        marginBottom: SPACING.lg,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        textAlign: 'center',
    },
    authorContainer: {
        marginBottom: SPACING.md,
        paddingHorizontal: SPACING.md,
        paddingVertical: 6,
        borderWidth: 1,
        borderColor: COLORS.secondary,
        borderRadius: 20,
        // backgroundColor: 'rgba(255,255,255,0.5)', // Optional subtle background for pill
    },
    authorText: {
        ...TYPOGRAPHY.caption,
        fontStyle: 'italic',
        color: COLORS.secondary,
        fontSize: 14,
        fontFamily: Platform.OS === 'ios' ? 'Georgia' : 'serif',
        fontWeight: '600',
    },
    // New Styles for Posts and FAB
    fab: {
        position: 'absolute',
        bottom: 50, // Increased to clear home indicator safely
        right: 30,
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: COLORS.accent, // Use accent from profile theme
        justifyContent: 'center',
        alignItems: 'center',
        ...SHADOWS.medium,
        shadowColor: COLORS.shadow,
        shadowOpacity: 0.4,
        elevation: 10,
        zIndex: 100, // Ensure it's on top
    },
    fabText: {
        fontSize: 34,
        color: COLORS.white,
        marginTop: -4,
    },
});
