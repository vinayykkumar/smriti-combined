import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Alert,
    KeyboardAvoidingView,
    Platform,
    ScrollView,
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../styles/theme';
import { API_BASE_URL } from '../constants/config';
import { useAuth } from '../hooks/useAuth';
import { Input, Button } from '../components';

export default function LoginScreen({ onBackToLanding }) {
    const { login } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    // Error states for inline validation
    const [usernameError, setUsernameError] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [serverError, setServerError] = useState('');

    const validateInputs = () => {
        // Clear previous errors
        setUsernameError('');
        setPasswordError('');
        setServerError('');

        let isValid = true;

        if (!username.trim()) {
            setUsernameError('Please enter your username');
            isValid = false;
        }
        if (!password) {
            setPasswordError('Please enter your password');
            isValid = false;
        }
        return isValid;
    };

    const handleLogin = async () => {
        if (!validateInputs()) return;

        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username.trim(),
                    password: password,
                }),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                const { token, ...userData } = data.data;
                // Use AuthContext login method - this will auto-redirect to home
                await login(userData, token);
            } else {
                setServerError(data.error || data.message || 'Invalid username or password');
            }
        } catch (error) {
            console.error('Login error:', error);
            setServerError('Unable to connect to server. Please check your internet connection.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.container}
        >
            <ScrollView
                contentContainerStyle={styles.scrollContent}
                keyboardShouldPersistTaps="handled"
            >
                {/* Header */}
                <View style={styles.header}>
                    <Text style={styles.logo}>🌳</Text>
                    <Text style={styles.title}>Welcome Back</Text>
                    <Text style={styles.subtitle}>Enter your details to continue</Text>
                </View>

                {/* Login Form */}
                <View style={styles.formContainer}>
                    {serverError ? (
                        <View style={styles.serverErrorContainer}>
                            <Text style={styles.serverErrorText}>{serverError}</Text>
                        </View>
                    ) : null}

                    <Input
                        label="Username"
                        value={username}
                        onChangeText={setUsername}
                        placeholder="Enter username"
                        error={usernameError}
                    />

                    <Input
                        label="Password"
                        value={password}
                        onChangeText={setPassword}
                        placeholder="Enter password"
                        secureTextEntry
                        error={passwordError}
                    />

                    <Button
                        title="Login"
                        onPress={handleLogin}
                        loading={loading}
                        style={{ marginTop: SPACING.md }}
                    />

                    <Button
                        title="← Back to Landing"
                        onPress={onBackToLanding}
                        variant="outline"
                        disabled={loading}
                        style={{ marginTop: SPACING.lg }}
                    />
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    scrollContent: {
        flexGrow: 1,
        padding: SPACING.lg,
        justifyContent: 'center',
    },
    header: {
        alignItems: 'center',
        marginBottom: SPACING.xl,
    },
    logo: {
        fontSize: 64,
        marginBottom: SPACING.sm,
    },
    title: {
        ...TYPOGRAPHY.title,
        fontSize: 32,
        fontWeight: '700',
        color: COLORS.primary,
        marginBottom: SPACING.xs,
    },
    subtitle: {
        ...TYPOGRAPHY.body,
        fontSize: 16,
        color: COLORS.secondary,
    },
    formContainer: {
        backgroundColor: COLORS.card,
        borderRadius: 16,
        padding: SPACING.lg,
        ...SHADOWS.medium,
    },
    inputGroup: {
        marginBottom: SPACING.md,
    },
    label: {
        ...TYPOGRAPHY.body,
        fontWeight: '500',
        marginBottom: SPACING.xs,
        color: COLORS.text,
    },
    input: {
        ...TYPOGRAPHY.body,
        borderWidth: 1,
        borderColor: COLORS.border,
        borderRadius: 8,
        padding: SPACING.md,
        backgroundColor: COLORS.background,
    },
    button: {
        backgroundColor: COLORS.primary,
        borderRadius: 8,
        padding: SPACING.md,
        alignItems: 'center',
        marginTop: SPACING.md,
        ...SHADOWS.small,
    },
    buttonDisabled: {
        opacity: 0.6,
    },
    buttonText: {
        ...TYPOGRAPHY.body,
        color: COLORS.background,
        fontWeight: '600',
    },
    backButton: {
        marginTop: SPACING.lg,
        alignItems: 'center',
    },
    backButtonText: {
        ...TYPOGRAPHY.caption,
        color: COLORS.secondary,
        fontWeight: '500',
    },
    serverErrorContainer: {
        backgroundColor: '#fee',
        padding: SPACING.md,
        borderRadius: 8,
        marginBottom: SPACING.md,
        borderLeftWidth: 4,
        borderLeftColor: '#f44',
    },
    serverErrorText: {
        color: '#c00',
        fontSize: 14,
    },
});
