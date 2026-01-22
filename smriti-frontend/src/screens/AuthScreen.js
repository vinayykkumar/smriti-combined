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
import { API_BASE_URL, MIN_USERNAME_LENGTH, MIN_PASSWORD_LENGTH } from '../constants/config';
import { useAuth } from '../hooks/useAuth';
import { Input, Button } from '../components';

export default function AuthScreen({ onBackToLanding }) {
    const { login } = useAuth();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);

    // Error states for inline validation
    const [usernameError, setUsernameError] = useState('');
    const [emailError, setEmailError] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [confirmPasswordError, setConfirmPasswordError] = useState('');
    const [serverError, setServerError] = useState('');

    const validateInputs = () => {
        // Clear previous errors
        setUsernameError('');
        setEmailError('');
        setPasswordError('');
        setConfirmPasswordError('');
        setServerError('');

        let isValid = true;

        if (!username.trim()) {
            setUsernameError('Please enter a username');
            isValid = false;
        } else if (username.trim().length < MIN_USERNAME_LENGTH) {
            setUsernameError(`Username must be at least ${MIN_USERNAME_LENGTH} characters`);
            isValid = false;
        }

        // Basic email validation
        if (!email.trim() || !email.includes('@')) { // Retaining original email validation logic
            setEmailError('Please enter a valid email address');
            isValid = false;
        }

        if (!password) {
            setPasswordError('Please enter a password');
            isValid = false;
        } else if (password.length < MIN_PASSWORD_LENGTH) {
            setPasswordError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters`);
            isValid = false;
        }

        if (password !== confirmPassword) {
            setConfirmPasswordError('Passwords do not match');
            isValid = false;
        }

        return isValid;
    };

    const handleSignUp = async () => {
        if (!validateInputs()) return;

        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username.trim(),
                    email: email.trim(),
                    password: password,
                }),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                const { token, ...userData } = data.data;

                // Clear form
                setUsername('');
                setEmail('');
                setPassword('');
                setConfirmPassword('');

                // Use AuthContext login method - this will auto-redirect to home
                await login(userData, token);
            } else {
                setServerError(data.error || data.message || 'Something went wrong');
            }
        } catch (error) {
            console.error('Sign up error:', error);
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
                    <Text style={styles.title}>Smriti</Text>
                    <Text style={styles.subtitle}>स्मृति</Text>
                    <Text style={styles.tagline}>A space for reflection</Text>
                </View>

                {/* Sign Up Form */}
                <View style={styles.formContainer}>
                    <Text style={styles.formTitle}>Create Account</Text>

                    {serverError ? (
                        <View style={styles.serverErrorContainer}>
                            <Text style={styles.serverErrorText}>{serverError}</Text>
                        </View>
                    ) : null}

                    <Input
                        label="Username"
                        value={username}
                        onChangeText={setUsername}
                        placeholder="Enter username (min 3 characters)"
                        error={usernameError}
                    />

                    <Input
                        label="Email"
                        value={email}
                        onChangeText={setEmail}
                        placeholder="Enter email address"
                        keyboardType="email-address"
                        error={emailError}
                    />

                    <Input
                        label="Password"
                        value={password}
                        onChangeText={setPassword}
                        placeholder="Enter password (min 6 characters)"
                        secureTextEntry
                        error={passwordError}
                    />

                    <Input
                        label="Confirm Password"
                        value={confirmPassword}
                        onChangeText={setConfirmPassword}
                        placeholder="Re-enter password"
                        secureTextEntry
                        error={confirmPasswordError}
                    />

                    <Button
                        title="Sign Up"
                        onPress={handleSignUp}
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

                    <Text style={styles.note}>
                        Note: This is Phase 1 - Sign up only. Login now available too!
                    </Text>
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
        marginBottom: SPACING.xxl,
    },
    logo: {
        fontSize: 64,
        marginBottom: SPACING.sm,
    },
    title: {
        ...TYPOGRAPHY.title,
        fontSize: 36,
        fontWeight: '700',
        color: COLORS.primary,
        marginBottom: SPACING.xs,
    },
    subtitle: {
        ...TYPOGRAPHY.heading,
        fontSize: 18,
        color: COLORS.secondary,
        marginBottom: SPACING.sm,
    },
    tagline: {
        ...TYPOGRAPHY.caption,
        fontStyle: 'italic',
    },
    formContainer: {
        backgroundColor: COLORS.card,
        borderRadius: 16,
        padding: SPACING.lg,
        ...SHADOWS.medium,
    },
    formTitle: {
        ...TYPOGRAPHY.heading,
        marginBottom: SPACING.lg,
        textAlign: 'center',
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
    note: {
        ...TYPOGRAPHY.caption,
        color: COLORS.textLight,
        textAlign: 'center',
        marginTop: SPACING.md,
        fontStyle: 'italic',
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
    backButton: {
        marginTop: SPACING.lg,
        alignItems: 'center',
    },
    backButtonText: {
        ...TYPOGRAPHY.caption,
        color: COLORS.secondary,
        fontWeight: '500',
    },
});
