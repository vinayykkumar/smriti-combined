import { StatusBar } from 'expo-status-bar';
import React, { useEffect } from 'react';
import { StyleSheet, View, Alert } from 'react-native';
import * as Updates from 'expo-updates';
import { NavigationContainer } from '@react-navigation/native';
import CreatePostScreen from './src/screens/CreatePostScreen';
import AuthScreen from './src/screens/AuthScreen';
import LandingScreen from './src/screens/LandingScreen';
import LoginScreen from './src/screens/LoginScreen';
import AppNavigator from './src/navigation/AppNavigator';
import { COLORS } from './src/styles/theme';
import { AuthProvider } from './src/contexts/AuthContext';
import { QuoteProvider } from './src/contexts/QuoteContext';
import { useAuth } from './src/hooks/useAuth';
import { useQuote } from './src/hooks/useQuote';
import QuotePopup from './src/components/common/QuotePopup';

// Inner content that needs QuoteContext
function AuthenticatedContent({ onLogout, onCreatePost, currentScreen, setCurrentScreen }) {
  const { isAuthenticated, token } = useAuth();
  const { openQuotePopup, clearQuoteData } = useQuote();
  const navigationRef = React.useRef(null);

  // Setup notification listeners when authenticated
  React.useEffect(() => {
    if (isAuthenticated && token) {
      const { setupNotificationListeners } = require('./src/services/notificationService');

      // Create a minimal navigation object for notification handlers
      const navigation = {
        navigate: (routeName) => {
          // Since we don't have direct access to React Navigation here,
          // we'll just reset to main screen when notification is tapped
          setCurrentScreen('MAIN');
        }
      };

      // Pass openQuotePopup for handling today_quote notifications
      const cleanup = setupNotificationListeners(navigation, token, {
        openQuotePopup
      });
      return cleanup;
    }
  }, [isAuthenticated, token, openQuotePopup]);

  // Clear quote data on logout
  React.useEffect(() => {
    if (!isAuthenticated) {
      clearQuoteData();
    }
  }, [isAuthenticated, clearQuoteData]);

  const handleLogout = async () => {
    await onLogout();
  };

  if (currentScreen === 'CREATE_POST') {
    return (
      <CreatePostScreen
        onCancel={() => setCurrentScreen('MAIN')}
        onSave={(post) => {
          setCurrentScreen('MAIN');
        }}
      />
    );
  }

  return (
    <NavigationContainer>
      <AppNavigator
        onCreatePost={onCreatePost}
        onLogout={handleLogout}
      />
      {/* Quote Popup - rendered inside NavigationContainer so it can use navigation */}
      <QuotePopup />
    </NavigationContainer>
  );
}

// Main App Content (uses auth context)
function AppContent() {
  const { isAuthenticated, isLoading, logout, token } = useAuth();
  const [currentScreen, setCurrentScreen] = React.useState('MAIN'); // 'MAIN' or 'CREATE_POST'
  const [authMode, setAuthMode] = React.useState('LANDING'); // 'LANDING', 'SIGN_UP', 'LOGIN'

  // Check for OTA updates on app launch
  useEffect(() => {
    async function checkForUpdates() {
      try {
        // Only check in production builds, not in dev mode
        if (!__DEV__) {
          const update = await Updates.checkForUpdateAsync();

          if (update.isAvailable) {
            Alert.alert(
              'Update Available',
              'A new version of the app is available. Would you like to update now?',
              [
                { text: 'Later', style: 'cancel' },
                {
                  text: 'Update Now',
                  onPress: async () => {
                    await Updates.fetchUpdateAsync();
                    await Updates.reloadAsync();
                  }
                }
              ]
            );
          }
        }
      } catch (error) {
        console.log('Error checking for updates:', error);
      }
    }

    checkForUpdates();
  }, []);

  const handleLogout = async () => {
    await logout();
    setAuthMode('LANDING');
    setCurrentScreen('MAIN');
  };

  return (
    <View style={styles.container}>
      <StatusBar style="dark" />
      {isLoading ? (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          {/* Loading state while checking auth */}
        </View>
      ) : isAuthenticated ? (
        <QuoteProvider>
          <AuthenticatedContent
            onLogout={handleLogout}
            onCreatePost={() => setCurrentScreen('CREATE_POST')}
            currentScreen={currentScreen}
            setCurrentScreen={setCurrentScreen}
          />
        </QuoteProvider>
      ) : authMode === 'LANDING' ? (
        <LandingScreen
          onSignUpPress={() => setAuthMode('SIGN_UP')}
          onLoginPress={() => setAuthMode('LOGIN')}
        />
      ) : authMode === 'SIGN_UP' ? (
        <AuthScreen
          onBackToLanding={() => setAuthMode('LANDING')}
        />
      ) : (
        <LoginScreen
          onBackToLanding={() => setAuthMode('LANDING')}
        />
      )}
    </View>
  );
}

// Root App Component with Provider
export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
});
