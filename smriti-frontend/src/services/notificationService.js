import { Platform, Alert } from 'react-native';
import { notifications } from './api';

// Only import Firebase messaging on native platforms (not web)
let messaging = null;
if (Platform.OS !== 'web') {
    try {
        messaging = require('@react-native-firebase/messaging').default;
    } catch (error) {
        console.warn('Firebase messaging not available:', error.message);
    }
}

/**
 * Request notification permission from the user
 * @returns {Promise<boolean>} true if permission granted, false otherwise
 */
export async function requestNotificationPermission() {
    // Web doesn't support Firebase messaging
    if (Platform.OS === 'web' || !messaging) {
        console.log('⚠️ Notifications not supported on web platform');
        return false;
    }

    try {
        const authStatus = await messaging().requestPermission();
        const enabled =
            authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
            authStatus === messaging.AuthorizationStatus.PROVISIONAL;

        if (enabled) {
            console.log('✅ Notification permission granted');
            return true;
        }
        console.log('❌ Notification permission denied');
        return false;
    } catch (error) {
        console.error('Error requesting notification permission:', error);
        return false;
    }
}

/**
 * Get FCM token and register it with the backend
 * @param {string} authToken - JWT authentication token
 * @returns {Promise<string|null>} FCM token if successful, null otherwise
 */
export async function registerDeviceToken(authToken) {
    if (Platform.OS === 'web' || !messaging) {
        console.log('⚠️ Device token registration not supported on web');
        return null;
    }

    try {
        // Get FCM token from Firebase
        const fcmToken = await messaging().getToken();
        console.log('📱 FCM Token retrieved:', fcmToken.substring(0, 20) + '...');

        // Register with backend
        await notifications.registerNotificationToken(fcmToken, Platform.OS);
        console.log('✅ Device registered for notifications');

        return fcmToken;
    } catch (error) {
        console.error('❌ Failed to register device token:', error);
        return null;
    }
}

/**
 * Unregister device token from backend
 * @param {string} authToken - JWT authentication token
 */
export async function unregisterDeviceToken(authToken) {
    if (Platform.OS === 'web' || !messaging) {
        console.log('⚠️ Device token unregistration not supported on web');
        return;
    }

    try {
        const fcmToken = await messaging().getToken();
        await notifications.unregisterNotificationToken(fcmToken, Platform.OS);
        console.log('✅ Device unregistered from notifications');
    } catch (error) {
        console.error('❌ Failed to unregister device token:', error);
    }
}

/**
 * Setup all notification event listeners
 * @param {object} navigation - React Navigation object for routing
 * @param {string} authToken - JWT authentication token for token refresh
 * @param {object} quoteCallbacks - Optional callbacks for quote notifications
 * @param {function} quoteCallbacks.openQuotePopup - Function to open quote popup
 * @returns {Function} Cleanup function to remove listeners
 */
export function setupNotificationListeners(navigation, authToken, quoteCallbacks = {}) {
    if (Platform.OS === 'web' || !messaging) {
        console.log('⚠️ Notification listeners not supported on web');
        return () => { }; // Return empty cleanup function
    }

    const unsubscribers = [];
    const { openQuotePopup } = quoteCallbacks;

    // 1. Handle foreground notifications (app is open)
    const unsubscribeForeground = messaging().onMessage(async (remoteMessage) => {
        console.log('📬 Notification received (foreground):', remoteMessage);

        // Handle Today's Quote notification - open popup directly
        if (remoteMessage.data?.type === 'today_quote') {
            console.log('📬 Today\'s Quote notification - opening popup');
            if (openQuotePopup) {
                openQuotePopup(true); // Force refresh
            }
            return;
        }

        // Default behavior for other notifications
        Alert.alert(
            remoteMessage.notification?.title || 'New Notification',
            remoteMessage.notification?.body || '',
            [
                {
                    text: 'View',
                    onPress: () => {
                        // Navigate to home or specific post if postId is provided
                        if (remoteMessage.data?.postId) {
                            navigation.navigate('Home'); // Can navigate to PostDetail if implemented
                        } else {
                            navigation.navigate('Home');
                        }
                    },
                },
                {
                    text: 'Dismiss',
                    style: 'cancel',
                },
            ]
        );
    });
    unsubscribers.push(unsubscribeForeground);

    // 2. Handle notification tap when app is in background
    const unsubscribeBackground = messaging().onNotificationOpenedApp(
        (remoteMessage) => {
            console.log('📬 Notification opened app from background:', remoteMessage);

            // Handle Today's Quote notification
            if (remoteMessage.data?.type === 'today_quote') {
                console.log('📬 Today\'s Quote notification (background) - opening popup');
                if (openQuotePopup) {
                    // Small delay to ensure app is ready
                    setTimeout(() => openQuotePopup(true), 300);
                }
                return;
            }

            // Navigate based on notification data
            if (remoteMessage.data?.postId) {
                navigation.navigate('Home'); // Can navigate to PostDetail if implemented
            } else {
                navigation.navigate('Home');
            }
        }
    );
    unsubscribers.push(unsubscribeBackground);

    // 3. Check if app was opened from notification (killed state)
    messaging()
        .getInitialNotification()
        .then((remoteMessage) => {
            if (remoteMessage) {
                console.log(
                    '📬 App opened from notification (killed state):',
                    remoteMessage
                );

                // Handle Today's Quote notification
                if (remoteMessage.data?.type === 'today_quote') {
                    console.log('📬 Today\'s Quote notification (killed) - opening popup');
                    if (openQuotePopup) {
                        // Longer delay to ensure app is fully ready
                        setTimeout(() => openQuotePopup(true), 500);
                    }
                    return;
                }

                // Navigate based on notification data
                if (remoteMessage.data?.postId) {
                    navigation.navigate('Home'); // Can navigate to PostDetail if implemented
                } else {
                    navigation.navigate('Home');
                }
            }
        });

    // 4. Handle token refresh
    const unsubscribeTokenRefresh = messaging().onTokenRefresh(async (newToken) => {
        console.log('🔄 FCM Token refreshed:', newToken.substring(0, 20) + '...');
        // Re-register with backend
        await registerDeviceToken(authToken);
    });
    unsubscribers.push(unsubscribeTokenRefresh);

    // Return cleanup function
    return () => {
        console.log('🧹 Cleaning up notification listeners');
        unsubscribers.forEach((unsubscribe) => unsubscribe());
    };
}

/**
 * Check if the device has notification permission
 * @returns {Promise<boolean>}
 */
export async function checkNotificationPermission() {
    if (Platform.OS === 'web' || !messaging) {
        return false;
    }

    const authStatus = await messaging().hasPermission();
    return (
        authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
        authStatus === messaging.AuthorizationStatus.PROVISIONAL
    );
}
