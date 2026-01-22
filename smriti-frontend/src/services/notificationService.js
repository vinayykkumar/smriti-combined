import messaging from '@react-native-firebase/messaging';
import { Platform, Alert } from 'react-native';
import { registerNotificationToken, unregisterNotificationToken } from './api';

/**
 * Request notification permission from the user
 * @returns {Promise<boolean>} true if permission granted, false otherwise
 */
export async function requestNotificationPermission() {
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
    try {
        // Get FCM token from Firebase
        const fcmToken = await messaging().getToken();
        console.log('📱 FCM Token retrieved:', fcmToken.substring(0, 20) + '...');

        // Register with backend
        await registerNotificationToken(fcmToken, Platform.OS);
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
    try {
        const fcmToken = await messaging().getToken();
        await unregisterNotificationToken(fcmToken, Platform.OS);
        console.log('✅ Device unregistered from notifications');
    } catch (error) {
        console.error('❌ Failed to unregister device token:', error);
    }
}

/**
 * Setup all notification event listeners
 * @param {object} navigation - React Navigation object for routing
 * @param {string} authToken - JWT authentication token for token refresh
 * @returns {Function} Cleanup function to remove listeners
 */
export function setupNotificationListeners(navigation, authToken) {
    const unsubscribers = [];

    // 1. Handle foreground notifications (app is open)
    const unsubscribeForeground = messaging().onMessage(async (remoteMessage) => {
        console.log('📬 Notification received (foreground):', remoteMessage);

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
    const authStatus = await messaging().hasPermission();
    return (
        authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
        authStatus === messaging.AuthorizationStatus.PROVISIONAL
    );
}
