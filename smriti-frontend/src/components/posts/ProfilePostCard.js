import React, { useState } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Linking, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { PROFILE_COLORS } from '../../styles/theme';

// Font family helper
const SERIF_FONT = Platform.OS === 'ios' ? 'Georgia' : 'serif';

/**
 * ProfilePostCard Component
 * Displays a single post item within the Profile Screen context.
 * Features:
 * - Dynamic image sizing (aspect ratio)
 * - Document attachment support
 * - "Received" footer status
 * - Options menu trigger
 */
export default function ProfilePostCard({ item, onOptionsPress }) {
    // Dynamic Image Sizing
    const [aspectRatio, setAspectRatio] = useState(4 / 3);
    const imageUrl = item.imageUrl || item.image_url;
    const documentUrl = item.documentUrl || item.document_url;

    React.useEffect(() => {
        if (imageUrl) {
            // Determine image size to prevent cropping
            Image.getSize(imageUrl, (width, height) => {
                if (width && height) {
                    setAspectRatio(width / height);
                }
            }, (error) => console.log("Image size calc error", error));
        }
    }, [imageUrl]);

    return (
        <View style={styles.postCard}>
            {/* Header: Title & Menu */}
            <View style={styles.cardHeader}>
                <View style={styles.cardTitleContainer}>
                    <Text style={styles.postTitle} numberOfLines={2}>{item.title}</Text>
                    <Text style={styles.postDateDetails}>
                        @{item.author?.username} • {new Date(item.createdAt || item.date).toLocaleDateString()}
                    </Text>
                </View>
                <TouchableOpacity
                    style={styles.optionsButton}
                    onPress={() => onOptionsPress(item.postId)}
                >
                    <Ionicons name="ellipsis-vertical" size={20} color={PROFILE_COLORS.textSecondary} />
                </TouchableOpacity>
            </View>

            {/* Content */}
            <Text style={styles.postContent}>{item.textContent || item.text_content}</Text>

            {/* Optional Image */}
            {imageUrl && (
                <Image
                    source={{ uri: imageUrl }}
                    style={[styles.postImage, { aspectRatio }]}
                    resizeMode="contain"
                />
            )}

            {/* Optional Document */}
            {documentUrl && (
                <TouchableOpacity
                    style={styles.documentContainer}
                    onPress={() => Linking.openURL(documentUrl)}
                >
                    <View style={styles.documentIconContainer}>
                        <Text style={styles.documentIcon}>📄</Text>
                    </View>
                    <View style={styles.documentInfo}>
                        <Text style={styles.documentTitle} numberOfLines={1}>
                            Attached Document
                        </Text>
                        <Text style={styles.documentAction}>Tap to view</Text>
                    </View>
                </TouchableOpacity>
            )}

            {/* Footer: Received Status */}
            <View style={styles.cardFooter}>
                <Ionicons name="sparkles-outline" size={16} color={PROFILE_COLORS.textSecondary} />
                <Text style={styles.footerText}>Received</Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    postCard: {
        backgroundColor: PROFILE_COLORS.card, // Lighter beige
        borderRadius: 16,
        padding: 24,
        marginBottom: 20,
        shadowColor: PROFILE_COLORS.shadow,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 12,
        elevation: 3,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 16,
    },
    cardTitleContainer: {
        flex: 1,
        paddingRight: 12,
    },
    postTitle: {
        fontSize: 20,
        color: PROFILE_COLORS.textPrimary,
        fontFamily: SERIF_FONT,
        marginBottom: 4,
        lineHeight: 28,
    },
    postDateDetails: {
        fontSize: 12,
        color: PROFILE_COLORS.textSecondary,
        fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif',
    },
    postImage: {
        width: '100%',
        backgroundColor: 'rgba(0,0,0,0.05)',
        marginBottom: 16,
        borderRadius: 8,
    },
    postContent: {
        fontSize: 15,
        color: PROFILE_COLORS.textPrimary,
        lineHeight: 24,
        marginBottom: 24,
        opacity: 0.9,
    },
    documentContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#FFF',
        padding: 12,
        borderRadius: 12,
        marginBottom: 24,
        borderWidth: 1,
        borderColor: PROFILE_COLORS.divider,
    },
    documentIconContainer: {
        width: 40,
        height: 40,
        backgroundColor: PROFILE_COLORS.card,
        borderRadius: 20,
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 12,
        borderWidth: 1,
        borderColor: PROFILE_COLORS.divider,
    },
    documentIcon: {
        fontSize: 20,
    },
    documentInfo: {
        flex: 1,
    },
    documentTitle: {
        fontSize: 14,
        fontWeight: '600',
        color: PROFILE_COLORS.textPrimary,
        marginBottom: 2,
        fontFamily: SERIF_FONT,
    },
    documentAction: {
        fontSize: 12,
        color: PROFILE_COLORS.accent,
    },
    cardFooter: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingTop: 16,
        borderTopWidth: 1,
        borderTopColor: PROFILE_COLORS.divider,
    },
    footerText: {
        marginLeft: 8,
        fontSize: 13,
        color: PROFILE_COLORS.textSecondary,
        fontFamily: SERIF_FONT,
    },
    optionsButton: {
        padding: 4,
    }
});
