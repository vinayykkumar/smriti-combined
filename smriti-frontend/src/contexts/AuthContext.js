import React, { createContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEY_USER_TOKEN, STORAGE_KEY_USER_DATA } from '../constants/config';

// Create the Auth Context
export const AuthContext = createContext();

/**
 * AuthProvider - Provides authentication state and methods to the entire app
 */
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // Check for existing auth on mount
    useEffect(() => {
        checkExistingAuth();
    }, []);

    const checkExistingAuth = async () => {
        try {
            const [storedToken, storedUserData] = await AsyncStorage.multiGet([
                STORAGE_KEY_USER_TOKEN,
                STORAGE_KEY_USER_DATA
            ]);

            const userToken = storedToken[1];
            const userData = storedUserData[1];

            if (userToken && userData) {
                setToken(userToken);
                setUser(JSON.parse(userData));
                setIsAuthenticated(true);
            }
        } catch (error) {
            console.error('Error checking auth:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (userData, authToken) => {
        try {
            await AsyncStorage.multiSet([
                [STORAGE_KEY_USER_TOKEN, authToken],
                [STORAGE_KEY_USER_DATA, JSON.stringify(userData)]
            ]);

            setToken(authToken);
            setUser(userData);
            setIsAuthenticated(true);

            // Setup push notifications after successful login
            try {
                const {
                    requestNotificationPermission,
                    registerDeviceToken
                } = require('../services/notificationService');

                const hasPermission = await requestNotificationPermission();
                if (hasPermission) {
                    await registerDeviceToken(authToken);
                }
            } catch (notifError) {
                // Don't block login if notification setup fails
                console.error('Failed to setup notifications:', notifError);
            }
        } catch (error) {
            console.error('Error during login:', error);
            throw error;
        }
    };

    const logout = async () => {
        try {
            // Unregister push notifications before logout
            try {
                const { unregisterDeviceToken } = require('../services/notificationService');
                await unregisterDeviceToken(token);
            } catch (notifError) {
                // Don't block logout if notification cleanup fails
                console.error('Failed to unregister notifications:', notifError);
            }

            await AsyncStorage.multiRemove([STORAGE_KEY_USER_TOKEN, STORAGE_KEY_USER_DATA]);
            setToken(null);
            setUser(null);
            setIsAuthenticated(false);
        } catch (error) {
            console.error('Error during logout:', error);
            throw error;
        }
    };

    const updateUser = async (updatedUserData) => {
        try {
            await AsyncStorage.setItem(STORAGE_KEY_USER_DATA, JSON.stringify(updatedUserData));
            setUser(updatedUserData);
        } catch (error) {
            console.error('Error updating user:', error);
            throw error;
        }
    };

    const value = {
        user,
        token,
        isLoading,
        isAuthenticated,
        login,
        logout,
        updateUser,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
