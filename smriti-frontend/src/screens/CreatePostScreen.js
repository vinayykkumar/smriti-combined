import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, ScrollView, Alert, Image, Dimensions, ActivityIndicator, Keyboard } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../styles/theme';
import { createPost } from '../services/api';

const { width } = Dimensions.get('window');

export default function CreatePostScreen({ onSave, onCancel }) {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [selectedImage, setSelectedImage] = useState(null);
    const [selectedDocument, setSelectedDocument] = useState(null);
    const [loading, setLoading] = useState(false);

    const pickImage = async () => {
        try {
            const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
            if (status !== 'granted') {
                Alert.alert('Permission needed', 'Gallery permission is required to select images.');
                return;
            }

            const result = await ImagePicker.launchImageLibraryAsync({
                mediaTypes: ImagePicker.MediaTypeOptions.Images,
                allowsEditing: false, // User wants original dimensions, no crop
                quality: 0.8,
            });
            if (!result.canceled && result.assets && result.assets.length > 0) {
                setSelectedImage(result.assets[0]);
            }
        } catch (error) {
            Alert.alert('Error', 'Failed to pick image');
        }
    };

    const pickDocument = async () => {
        try {
            const result = await DocumentPicker.getDocumentAsync({
                type: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
                copyToCacheDirectory: true,
            });
            if (!result.canceled && result.assets && result.assets.length > 0) {
                const doc = result.assets[0];
                if (doc.size && doc.size > 10 * 1024 * 1024) {
                    Alert.alert('File Too Large', 'Please select a document smaller than 10MB.');
                    return;
                }
                setSelectedDocument(doc);
            }
        } catch (error) {
            Alert.alert('Error', 'Failed to pick document');
        }
    };

    const handleSave = async () => {
        Keyboard.dismiss();
        if (!title.trim() && !description.trim() && !selectedImage && !selectedDocument) {
            Alert.alert('Empty Post', 'Please add some content to your post.');
            return;
        }

        setLoading(true);
        try {
            const postData = {};
            if (title.trim()) postData.title = title.trim();
            if (description.trim()) postData.textContent = description.trim();
            if (selectedImage) postData.image = selectedImage;
            if (selectedDocument) postData.document = selectedDocument;

            const result = await createPost(postData);

            if (result.success) {
                if (onSave) onSave();
            } else {
                Alert.alert('Error', result.error || 'Failed to create post');
            }
        } catch (error) {
            Alert.alert('Error', 'An unexpected error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleBackPress = () => {
        if (title.trim() || description.trim() || selectedImage || selectedDocument) {
            Alert.alert(
                'Discard Reflection?',
                'Are you sure you want to discard this post? Changes will be lost.',
                [
                    { text: 'Cancel', style: 'cancel' },
                    { text: 'Discard', style: 'destructive', onPress: onCancel }
                ]
            );
        } else {
            onCancel(); // No content, just go back
        }
    };

    return (
        <View style={styles.container}>
            {/* Background Texture Simulation via Color Overlay */}
            <View style={styles.backgroundLayer} />

            {/* Custom Header: Back & Share */}
            <View style={styles.header}>
                <TouchableOpacity onPress={handleBackPress} style={styles.backButton}>
                    <Ionicons name="arrow-back" size={24} color="#5C4033" />
                </TouchableOpacity>

                <TouchableOpacity
                    style={[styles.smallShareButton, (!title.trim() && !description.trim()) && styles.disabledButton]}
                    onPress={handleSave}
                    disabled={loading || (!title.trim() && !description.trim())}
                >
                    {loading ? (
                        <ActivityIndicator color="#FFF" size="small" />
                    ) : (
                        <Text style={styles.smallShareText}>Share</Text>
                    )}
                </TouchableOpacity>
            </View>

            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                style={styles.keyboardView}
            >
                <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>



                    {/* Title Input (Pill Shape) */}
                    <View style={styles.titleContainer}>
                        <TextInput
                            style={styles.titleInput}
                            placeholder="If all your thoughts came down to one line…"
                            placeholderTextColor="#9C8C74"
                            value={title}
                            onChangeText={setTitle}
                            maxLength={100}
                        />
                    </View>

                    {/* Main Content Area (Large Container) */}
                    <View style={styles.contentCard}>
                        <TextInput
                            style={styles.contentInput}
                            placeholder="Let your thoughts unfold here..."
                            placeholderTextColor="#9C8C74"
                            value={description}
                            onChangeText={setDescription}
                            multiline
                            textAlignVertical="top"
                        />

                        {/* Attachments List inside key area */}
                        <View style={styles.attachmentsList}>
                            {selectedImage && (
                                <View style={styles.attachmentItem}>
                                    <View style={styles.attachmentIconBox}>
                                        <Image source={{ uri: selectedImage.uri }} style={styles.attachmentThumb} />
                                    </View>
                                    <Text style={styles.attachmentName} numberOfLines={1}>image.jpg</Text>
                                    <TouchableOpacity onPress={() => setSelectedImage(null)} style={styles.removeButton}>
                                        <Text style={styles.removeIcon}>×</Text>
                                    </TouchableOpacity>
                                </View>
                            )}

                            {selectedDocument && (
                                <View style={styles.attachmentItem}>
                                    <View style={styles.attachmentIconBox}>
                                        <Text style={styles.docIcon}>📄</Text>
                                    </View>
                                    <Text style={styles.attachmentName} numberOfLines={1}>{selectedDocument.name}</Text>
                                    <TouchableOpacity onPress={() => setSelectedDocument(null)} style={styles.removeButton}>
                                        <Text style={styles.removeIcon}>×</Text>
                                    </TouchableOpacity>
                                </View>
                            )}
                        </View>

                        {/* Attachment Buttons Bar - Inside the card at the bottom */}
                        <View style={styles.toolbarContainer}>
                            <TouchableOpacity style={styles.toolButton} onPress={pickImage}>
                                <Text style={styles.toolIcon}>＋</Text>
                                <Text style={styles.toolText}>Image</Text>
                            </TouchableOpacity>

                            <TouchableOpacity style={styles.toolButton} onPress={pickDocument}>
                                <Text style={styles.toolIcon}>📎</Text>
                                <Text style={styles.toolText}>Document</Text>
                            </TouchableOpacity>

                            <TouchableOpacity style={styles.toolButton} onPress={() => { }}>
                                <Text style={styles.toolIcon}>🔗</Text>
                                <Text style={styles.toolText}>Link</Text>
                            </TouchableOpacity>
                        </View>
                    </View>

                </ScrollView>


            </KeyboardAvoidingView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#EBE2D7', // Texture base color
    },
    backgroundLayer: {
        ...StyleSheet.absoluteFillObject,
        backgroundColor: '#F2ECE4', // Light warm overly
        opacity: 0.6,
    },
    keyboardView: {
        flex: 1,
    },
    scrollContent: {
        padding: SPACING.lg,
        paddingBottom: 40,
    },

    titleContainer: {
        marginBottom: SPACING.lg,
        marginTop: SPACING.sm, // Reduced since header takes space
    },
    titleInput: {
        backgroundColor: 'rgba(255, 255, 255, 0.4)',
        borderRadius: 24, // Pill shape
        paddingHorizontal: SPACING.xl,
        paddingVertical: 14,
        fontSize: 14,
        color: '#4A4036',
        borderWidth: 1,
        borderColor: 'rgba(139, 115, 85, 0.15)',
    },
    contentCard: {
        backgroundColor: 'rgba(255, 255, 255, 0.5)', // Translucent glass effect
        borderRadius: 24,
        padding: SPACING.lg,
        minHeight: 450,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.6)',
        justifyContent: 'space-between', // Push toolbar to bottom
    },
    contentInput: {
        fontSize: 14,
        color: '#4A4036',
        flex: 1,
        marginBottom: SPACING.xl,
        textAlignVertical: 'top',
    },
    attachmentsList: {
        marginBottom: SPACING.md,
    },
    attachmentItem: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.6)',
        padding: 8,
        borderRadius: 12,
        marginBottom: 8,
        borderWidth: 1,
        borderColor: 'rgba(139, 115, 85, 0.1)',
    },
    attachmentIconBox: {
        width: 36,
        height: 36,
        borderRadius: 8,
        overflow: 'hidden',
        marginRight: 10,
        backgroundColor: '#E0D5C5',
        alignItems: 'center',
        justifyContent: 'center',
    },
    attachmentThumb: {
        width: '100%',
        height: '100%',
    },
    docIcon: {
        fontSize: 20,
    },
    attachmentName: {
        flex: 1,
        fontSize: 14,
        color: '#5C4033',
        fontWeight: '500',
    },
    removeButton: {
        padding: 8,
    },
    removeIcon: {
        fontSize: 18,
        color: '#8B7355',
        fontWeight: 'bold', // Thick cross
    },
    toolbarContainer: {
        flexDirection: 'row',
        gap: 10,
        paddingTop: SPACING.sm,
    },
    toolButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255, 248, 240, 0.5)',
        paddingVertical: 10,
        paddingHorizontal: 16,
        borderRadius: 20,
        borderWidth: 1,
        borderColor: 'rgba(139, 115, 85, 0.2)',
    },
    toolIcon: {
        fontSize: 14,
        color: '#5C4033',
        marginRight: 6,
    },
    toolText: {
        fontSize: 14,
        color: '#5C4033',
        fontWeight: '500',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: SPACING.lg,
        paddingTop: Platform.OS === 'ios' ? 60 : 50,
        paddingBottom: SPACING.sm,
        zIndex: 10,
    },
    backButton: {
        padding: 8,
        marginLeft: -8,
    },
    smallShareButton: {
        backgroundColor: '#988574', // Muted Earth Brown
        paddingVertical: 8,
        paddingHorizontal: 20,
        borderRadius: 20,
        shadowColor: '#5C4033',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 4,
        elevation: 3,
    },
    disabledButton: {
        opacity: 0.5,
    },
    smallShareText: {
        fontSize: 14,
        color: '#FFFFFF',
        fontWeight: '600',
    },
});
