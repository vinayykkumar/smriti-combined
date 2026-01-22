import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Platform } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../styles/theme';

export default function LandingScreen({ onSignUpPress, onLoginPress }) {
    return (
        <View style={styles.container}>
            <View style={styles.content}>
                {/* Logo Section */}
                <View style={styles.logoContainer}>
                    <Image
                        source={require('../../assets/smriti_logo.png')}
                        style={styles.logo}
                        resizeMode="contain"
                    />
                    <Text style={styles.title}>Smriti</Text>
                    <Text style={styles.subtitle}>Memory & Reflection v1.1</Text>
                </View>

                {/* Action Buttons */}
                <View style={styles.buttonContainer}>
                    <TouchableOpacity style={styles.primaryButton} onPress={onSignUpPress}>
                        <Text style={styles.primaryButtonText}>Sign Up</Text>
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.secondaryButton} onPress={onLoginPress}>
                        <Text style={styles.secondaryButtonText}>Login</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
        justifyContent: 'center',
        padding: SPACING.lg,
    },
    content: {
        flex: 1,
        justifyContent: 'space-around',
        alignItems: 'center',
        paddingVertical: SPACING.xl,
    },
    logoContainer: {
        alignItems: 'center',
        marginTop: SPACING.xl,
    },
    logo: {
        width: 200,
        height: 200,
        marginBottom: SPACING.md,
    },
    title: {
        fontSize: 48,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginBottom: SPACING.xs,
        fontFamily: Platform.OS === 'ios' ? 'Serif' : 'serif', // Trying to get a more elegant font
    },
    subtitle: {
        ...TYPOGRAPHY.body,
        fontSize: 18,
        color: COLORS.secondary,
        fontStyle: 'italic',
        letterSpacing: 1,
    },
    buttonContainer: {
        width: '100%',
        gap: SPACING.md,
        marginBottom: SPACING.xl,
    },
    primaryButton: {
        backgroundColor: COLORS.primary,
        paddingVertical: SPACING.md,
        borderRadius: 30,
        alignItems: 'center',
        ...SHADOWS.medium,
    },
    primaryButtonText: {
        color: COLORS.background,
        fontSize: 18,
        fontWeight: '600',
    },
    secondaryButton: {
        backgroundColor: 'transparent',
        paddingVertical: SPACING.md,
        borderRadius: 30,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: COLORS.primary,
    },
    secondaryButtonText: {
        color: COLORS.primary,
        fontSize: 18,
        fontWeight: '600',
    },
});
