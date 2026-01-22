import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    Alert,
    Modal,
    ActivityIndicator,
    RefreshControl,
    Platform,
    TouchableWithoutFeedback,
    ImageBackground,
    Image,
    Linking
} from 'react-native';
import { useProfile } from '../hooks/useProfile';
import { Ionicons } from '@expo/vector-icons';
import { PROFILE_COLORS } from '../styles/theme';
import ProfilePostCard from '../components/posts/ProfilePostCard';

const PROFILE_THEME = PROFILE_COLORS; // Alias for backward compatibility in this file

// Font family helper
const SERIF_FONT = Platform.OS === 'ios' ? 'Georgia' : 'serif';

export default function ProfileScreen({ onLogout }) {
    const { user, posts, loading, refreshing, error, refreshProfile, removePost } = useProfile();
    const [optionsModalVisible, setOptionsModalVisible] = useState(false);
    const [deleteModalVisible, setDeleteModalVisible] = useState(false);
    const [selectedPostId, setSelectedPostId] = useState(null);
    const [settingsMenuVisible, setSettingsMenuVisible] = useState(false);

    const handleLogoutPress = () => {
        Alert.alert(
            'Logout',
            'Are you sure you want to logout?',
            [
                { text: 'Cancel', style: 'cancel' },
                { text: 'Logout', onPress: onLogout, style: 'destructive' }
            ]
        );
    };

    const handleOptionsPress = (postId) => {
        setSelectedPostId(postId);
        setOptionsModalVisible(true);
    };

    const handleEditPress = () => {
        setOptionsModalVisible(false);
        Alert.alert('Coming Soon', 'Edit functionality will be available in the next update.');
    };

    const handleDeleteOptionPress = () => {
        setOptionsModalVisible(false);
        setTimeout(() => setDeleteModalVisible(true), 100);
    };

    const handleConfirmDelete = async () => {
        if (!selectedPostId) return;

        setDeleteModalVisible(false);
        const result = await removePost(selectedPostId);

        if (!result.success) {
            Alert.alert('Error', result.error || 'Failed to delete post');
        }

        setSelectedPostId(null);
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    };

    const renderHeader = () => {
        if (loading && !user) {
            return (
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color={PROFILE_THEME.accent} />
                </View>
            );
        }

        if (!user) return null;

        const initial = user.username.charAt(0).toUpperCase();
        const memberSince = formatDate(user.joined_at);

        return (
            <View style={styles.headerContainer}>
                {/* Settings Icon - Top Right */}
                <TouchableOpacity
                    style={styles.settingsIconButton}
                    onPress={() => setSettingsMenuVisible(true)}
                >
                    <Ionicons name="settings-outline" size={24} color={PROFILE_THEME.textSecondary} />
                </TouchableOpacity>

                {/* Avatar */}
                <View style={styles.avatarContainer}>
                    <View style={styles.avatar}>
                        <Text style={styles.avatarText}>{initial}</Text>
                    </View>
                </View>

                {/* Username & Tagline */}
                <Text style={styles.username}>@{user.username}</Text>
                <Text style={styles.tagline}>Remember gently.</Text>

                {/* Meta Row: Reflections . 1 | Since . Jan 2026 */}
                <View style={styles.metaRow}>
                    <Text style={styles.metaText}>Reflections • {user.post_count}</Text>
                    <View style={styles.metaDivider} />
                    <Text style={styles.metaText}>Since • {memberSince}</Text>
                </View>
            </View>
        );
    };



    const renderEmptyState = () => (
        <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No reflections yet.</Text>
            <Text style={styles.emptySubText}>Take a moment to write one.</Text>
        </View>
    );

    const backgroundImage = require('../../assets/bg_profile_page.png');

    return (
        <ImageBackground
            source={backgroundImage}
            style={styles.container}
            resizeMode="cover"
        >
            <ScrollView
                contentContainerStyle={styles.scrollContent}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={refreshProfile}
                        tintColor={PROFILE_THEME.accent}
                    />
                }
            >
                {renderHeader()}

                {error && (
                    <View style={styles.errorContainer}>
                        <Text style={styles.errorText}>{error}</Text>
                    </View>
                )}

                <View style={styles.featuredSection}>
                    <Text style={styles.sectionHeader}>My Reflections</Text>
                    {posts.length === 0 && !loading ? (
                        renderEmptyState()
                    ) : (
                        posts.map((post) => (
                            <ProfilePostCard
                                key={post.postId || post.id}
                                item={post}
                                onOptionsPress={handleOptionsPress}
                            />
                        ))
                    )}
                </View>


            </ScrollView>

            {/* Options Menu Modal */}
            <Modal
                visible={optionsModalVisible}
                transparent
                animationType="fade"
                onRequestClose={() => setOptionsModalVisible(false)}
            >
                <TouchableOpacity
                    style={styles.modalOverlay}
                    activeOpacity={1}
                    onPress={() => setOptionsModalVisible(false)}
                >
                    <TouchableWithoutFeedback>
                        <View style={styles.centeredMenuCard}>
                            <View style={styles.menuHandle} />

                            <TouchableOpacity style={styles.menuItem} onPress={handleEditPress}>
                                <Ionicons name="pencil-outline" size={22} color={PROFILE_THEME.textPrimary} />
                                <Text style={styles.menuItemText}>Edit</Text>
                            </TouchableOpacity>

                            <TouchableOpacity style={styles.menuItem} onPress={() => Alert.alert('Coming Soon', 'Pin feature coming soon')}>
                                <Ionicons name="pin-outline" size={22} color={PROFILE_THEME.textPrimary} />
                                <Text style={styles.menuItemText}>Pin</Text>
                            </TouchableOpacity>

                            <TouchableOpacity style={styles.menuItem} onPress={() => Alert.alert('Coming Soon', 'Share feature coming soon')}>
                                <Ionicons name="share-outline" size={22} color={PROFILE_THEME.textPrimary} />
                                <Text style={styles.menuItemText}>Share</Text>
                            </TouchableOpacity>

                            <TouchableOpacity style={styles.menuItem} onPress={() => Alert.alert('Coming Soon', 'Export feature coming soon')}>
                                <Ionicons name="document-text-outline" size={22} color={PROFILE_THEME.textPrimary} />
                                <Text style={styles.menuItemText}>Export</Text>
                            </TouchableOpacity>

                            <View style={styles.menuDivider} />

                            <TouchableOpacity style={styles.menuItem} onPress={handleDeleteOptionPress}>
                                <Ionicons name="trash-outline" size={22} color="#8B0000" />
                                <Text style={[styles.menuItemText, styles.menuDestructiveText]}>Delete</Text>
                            </TouchableOpacity>
                        </View>
                    </TouchableWithoutFeedback>
                </TouchableOpacity>
            </Modal>

            {/* Delete Confirmation Modal */}
            <Modal
                visible={deleteModalVisible}
                transparent
                animationType="fade"
                onRequestClose={() => setDeleteModalVisible(false)}
            >
                <TouchableOpacity
                    style={styles.centeredOverlay}
                    activeOpacity={1}
                    onPress={() => setDeleteModalVisible(false)}
                >
                    <TouchableWithoutFeedback>
                        <View style={styles.modalContent}>
                            <Text style={styles.modalTitle}>Delete Reflection?</Text>
                            <Text style={styles.modalText}>
                                Are you sure you want to delete this reflection? This action cannot be undone.
                            </Text>
                            <View style={styles.modalButtons}>
                                <TouchableOpacity
                                    style={[styles.modalButton, styles.cancelButton]}
                                    onPress={() => setDeleteModalVisible(false)}
                                >
                                    <Text style={styles.cancelButtonText}>Cancel</Text>
                                </TouchableOpacity>
                                <TouchableOpacity
                                    style={[styles.modalButton, styles.deleteButton]}
                                    onPress={handleConfirmDelete}
                                >
                                    <Text style={styles.deleteButtonText}>Delete</Text>
                                </TouchableOpacity>
                            </View>
                        </View>
                    </TouchableWithoutFeedback>
                </TouchableOpacity>
            </Modal>

            {/* Settings Bottom Sheet - 3x3 Grid Menu */}
            <Modal
                visible={settingsMenuVisible}
                transparent
                animationType="slide"
                onRequestClose={() => setSettingsMenuVisible(false)}
            >
                <View style={styles.gridMenuOverlay}>
                    <TouchableOpacity
                        style={{ flex: 1 }}
                        activeOpacity={1}
                        onPress={() => setSettingsMenuVisible(false)}
                    />
                    <View style={styles.gridMenuContainer}>
                        {/* Header */}
                        <View style={styles.gridMenuHeader}>
                            <View style={styles.menuHandle} />
                            <Text style={styles.gridMenuTitle}>Menu</Text>
                        </View>

                        {/* 3x3 Grid */}
                        <View style={styles.menuGrid}>
                            {/* Row 1 */}
                            <TouchableOpacity
                                style={styles.gridTile}
                                onPress={() => {
                                    setSettingsMenuVisible(false);
                                    Alert.alert('Info', 'Edit Profile coming soon');
                                }}
                            >
                                <View style={styles.gridIconContainer}>
                                    <Ionicons name="create-outline" size={28} color={PROFILE_THEME.textPrimary} />
                                </View>
                                <Text style={styles.gridTileText}>Edit Profile</Text>
                            </TouchableOpacity>

                            <TouchableOpacity
                                style={styles.gridTile}
                                onPress={() => {
                                    setSettingsMenuVisible(false);
                                    Alert.alert('Info', 'Preferences coming soon');
                                }}
                            >
                                <View style={styles.gridIconContainer}>
                                    <Ionicons name="options-outline" size={28} color={PROFILE_THEME.textPrimary} />
                                </View>
                                <Text style={styles.gridTileText}>Settings</Text>
                            </TouchableOpacity>

                            <TouchableOpacity
                                style={styles.gridTile}
                                onPress={() => {
                                    setSettingsMenuVisible(false);
                                    Alert.alert('Info', 'Notifications coming soon');
                                }}
                            >
                                <View style={styles.gridIconContainer}>
                                    <Ionicons name="notifications-outline" size={28} color={PROFILE_THEME.textPrimary} />
                                </View>
                                <Text style={styles.gridTileText}>Notifications</Text>
                            </TouchableOpacity>

                            {/* Row 2 */}
                            <TouchableOpacity
                                style={styles.gridTile}
                                onPress={() => {
                                    setSettingsMenuVisible(false);
                                    Alert.alert('Info', 'Privacy settings coming soon');
                                }}
                            >
                                <View style={styles.gridIconContainer}>
                                    <Ionicons name="lock-closed-outline" size={28} color={PROFILE_THEME.textPrimary} />
                                </View>
                                <Text style={styles.gridTileText}>Privacy</Text>
                            </TouchableOpacity>

                            <TouchableOpacity
                                style={styles.gridTile}
                                onPress={() => {
                                    setSettingsMenuVisible(false);
                                    Alert.alert('Info', 'Help & Support coming soon');
                                }}
                            >
                                <View style={styles.gridIconContainer}>
                                    <Ionicons name="help-circle-outline" size={28} color={PROFILE_THEME.textPrimary} />
                                </View>
                                <Text style={styles.gridTileText}>Help</Text>
                            </TouchableOpacity>

                            <TouchableOpacity
                                style={styles.gridTile}
                                onPress={() => {
                                    setSettingsMenuVisible(false);
                                    Alert.alert('Info', 'About Smriti v1.0.0');
                                }}
                            >
                                <View style={styles.gridIconContainer}>
                                    <Ionicons name="information-circle-outline" size={28} color={PROFILE_THEME.textPrimary} />
                                </View>
                                <Text style={styles.gridTileText}>About</Text>
                            </TouchableOpacity>

                            {/* Row 3 */}
                            <TouchableOpacity
                                style={styles.gridTile}
                                onPress={() => {
                                    setSettingsMenuVisible(false);
                                    Alert.alert('Info', 'Share coming soon');
                                }}
                            >
                                <View style={styles.gridIconContainer}>
                                    <Ionicons name="share-social-outline" size={28} color={PROFILE_THEME.textPrimary} />
                                </View>
                                <Text style={styles.gridTileText}>Share</Text>
                            </TouchableOpacity>

                            <TouchableOpacity
                                style={styles.gridTile}
                                onPress={() => {
                                    setSettingsMenuVisible(false);
                                    Alert.alert('Info', 'Rate Us coming soon');
                                }}
                            >
                                <View style={styles.gridIconContainer}>
                                    <Ionicons name="star-outline" size={28} color={PROFILE_THEME.textPrimary} />
                                </View>
                                <Text style={styles.gridTileText}>Rate Us</Text>
                            </TouchableOpacity>

                            <TouchableOpacity
                                style={styles.gridTile}
                                onPress={() => {
                                    setSettingsMenuVisible(false);
                                    handleLogoutPress();
                                }}
                            >
                                <View style={[styles.gridIconContainer, { backgroundColor: '#FFE5E5' }]}>
                                    <Ionicons name="log-out-outline" size={28} color="#8B0000" />
                                </View>
                                <Text style={[styles.gridTileText, { color: '#8B0000' }]}>Sign Out</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </View>
            </Modal>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        // backgroundColor: PROFILE_THEME.background, // Removed for ImageBackground
        paddingTop: 60,
    },
    scrollContent: {
        paddingBottom: 80,
    },
    loadingContainer: {
        padding: 40,
        alignItems: 'center',
    },
    headerContainer: {
        alignItems: 'center',
        marginBottom: 30,
    },
    avatarContainer: {
        marginBottom: 16,
        shadowColor: PROFILE_THEME.shadow,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 10,
        elevation: 8,
    },
    avatar: {
        width: 100,
        height: 100,
        borderRadius: 50,
        backgroundColor: PROFILE_THEME.accent,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 4,
        borderColor: 'rgba(255,255,255,0.2)',
    },
    avatarText: {
        fontSize: 40,
        color: PROFILE_THEME.white,
        fontFamily: SERIF_FONT,
    },
    username: {
        fontSize: 24,
        color: PROFILE_THEME.textPrimary,
        fontFamily: SERIF_FONT,
        marginBottom: 4,
    },
    tagline: {
        fontSize: 16,
        color: PROFILE_THEME.textSecondary,
        fontFamily: SERIF_FONT,
        fontStyle: 'italic',
        marginBottom: 16,
    },
    metaRow: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    metaText: {
        fontSize: 14,
        color: PROFILE_THEME.textSecondary,
        opacity: 0.8,
    },
    metaDivider: {
        width: 1,
        height: 12,
        backgroundColor: PROFILE_THEME.divider,
        marginHorizontal: 12,
    },
    featuredSection: {
        paddingHorizontal: 20,
        marginBottom: 40,
    },
    sectionHeader: {
        fontSize: 16,
        color: PROFILE_THEME.textSecondary,
        marginBottom: 12,
        fontFamily: SERIF_FONT,
    },

    settingsSection: {
        paddingHorizontal: 20,
    },
    settingsContainer: {
        backgroundColor: 'rgba(255, 255, 255, 0.4)', // Glass-like feel
        borderRadius: 20,
        overflow: 'hidden',
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.6)',
    },
    settingItem: {
        paddingVertical: 16,
        paddingHorizontal: 20,
        alignItems: 'center',
    },
    settingText: {
        fontSize: 16,
        color: PROFILE_THEME.textPrimary,
        fontFamily: SERIF_FONT,
    },
    settingDivider: {
        height: 1,
        backgroundColor: PROFILE_THEME.divider,
        opacity: 0.5,
    },
    versionText: {
        textAlign: 'center',
        marginTop: 20,
        color: PROFILE_THEME.textSecondary,
        fontSize: 12,
        opacity: 0.6,
    },
    emptyContainer: {
        padding: 40,
        alignItems: 'center',
        backgroundColor: PROFILE_THEME.card,
        borderRadius: 16,
    },
    emptyText: {
        fontSize: 16,
        color: PROFILE_THEME.textSecondary,
        fontFamily: SERIF_FONT,
        marginBottom: 8,
    },
    emptySubText: {
        fontSize: 14,
        color: PROFILE_THEME.textSecondary,
        opacity: 0.6,
    },
    // Modal Styles
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.3)', // Lighter overlay for gentler feel
        justifyContent: 'flex-end',
        alignItems: 'center',
    },
    centeredMenuCard: {
        backgroundColor: PROFILE_THEME.card,
        borderRadius: 24,
        padding: 24,
        width: '90%',
        maxWidth: 400,
        alignItems: 'center',
        marginBottom: 80, // High float
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.1,
        shadowRadius: 20,
        elevation: 10,
    },
    menuHandle: {
        width: 40,
        height: 4,
        backgroundColor: PROFILE_THEME.divider,
        borderRadius: 2,
        marginBottom: 24,
    },
    menuItem: {
        flexDirection: 'row',
        alignItems: 'center',
        width: '100%',
        paddingVertical: 14,
        paddingHorizontal: 8,
        gap: 16,
    },
    menuItemText: {
        fontSize: 17,
        color: PROFILE_THEME.textPrimary,
        fontFamily: SERIF_FONT,
    },
    menuDivider: {
        width: '100%',
        height: 1,
        backgroundColor: PROFILE_THEME.divider,
        marginVertical: 8,
        opacity: 0.5,
    },
    menuDestructiveText: {
        color: '#8B0000',
    },
    modalContent: {
        backgroundColor: PROFILE_THEME.card,
        borderRadius: 20,
        padding: 24,
        width: '80%',
        maxWidth: 350,
        elevation: 5,
    },
    modalTitle: {
        fontSize: 20,
        fontFamily: SERIF_FONT,
        color: PROFILE_THEME.textPrimary,
        marginBottom: 12,
    },
    modalText: {
        fontSize: 16,
        color: PROFILE_THEME.textSecondary,
        marginBottom: 24,
        lineHeight: 22,
    },
    modalButtons: {
        flexDirection: 'row',
        gap: 12,
    },
    modalButton: {
        flex: 1,
        padding: 12,
        borderRadius: 10,
        alignItems: 'center',
        justifyContent: 'center',
    },
    cancelButton: {
        backgroundColor: PROFILE_THEME.divider,
    },
    deleteButton: {
        backgroundColor: '#A1887F', // softer brown-red
    },
    cancelButtonText: {
        color: PROFILE_THEME.textPrimary,
        fontWeight: '600',
    },
    deleteButtonText: {
        color: PROFILE_THEME.white,
        fontWeight: '600',
    },
    errorContainer: {
        backgroundColor: '#FFE5E5',
        padding: 10,
        margin: 20,
        borderRadius: 8,
    },
    errorText: {
        color: '#D32F2F',
        textAlign: 'center',
    },
    // Settings Icon Button
    settingsIconButton: {
        position: 'absolute',
        top: 0,
        right: 20,
        padding: 8,
        zIndex: 10,
    },
    // Settings Grid Menu Styles
    gridMenuOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'flex-end',
    },
    centeredOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    gridMenuContainer: {
        backgroundColor: PROFILE_THEME.card,
        borderTopLeftRadius: 24,
        borderTopRightRadius: 24,
        paddingTop: 12,
        paddingBottom: 40,
        paddingHorizontal: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -4 },
        shadowOpacity: 0.15,
        shadowRadius: 12,
        elevation: 10,
    },
    gridMenuHeader: {
        alignItems: 'center',
        marginBottom: 24,
    },
    gridMenuTitle: {
        fontSize: 20,
        fontFamily: SERIF_FONT,
        color: PROFILE_THEME.textPrimary,
        fontWeight: '600',
        marginTop: 12,
    },
    menuGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        gap: 16,
    },
    gridTile: {
        width: '30%', // 3 columns
        aspectRatio: 1, // Square tiles
        backgroundColor: PROFILE_THEME.background,
        borderRadius: 16,
        alignItems: 'center',
        justifyContent: 'center',
        padding: 12,
        shadowColor: PROFILE_THEME.shadow,
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    gridIconContainer: {
        width: 48,
        height: 48,
        borderRadius: 24,
        backgroundColor: 'rgba(141, 110, 99, 0.1)', // Light accent
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 8,
    },
    gridTileText: {
        fontSize: 12,
        color: PROFILE_THEME.textPrimary,
        fontFamily: SERIF_FONT,
        textAlign: 'center',
    },
});
