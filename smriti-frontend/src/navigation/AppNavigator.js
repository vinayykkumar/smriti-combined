import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';
import HomeScreen from '../screens/HomeScreen';
import ProfileScreen from '../screens/ProfileScreen';
import SearchScreen from '../screens/SearchScreen';
import UserProfileScreen from '../screens/UserProfileScreen';
import PastQuotesScreen from '../screens/PastQuotesScreen';
import CirclesListScreen from '../screens/CirclesListScreen';
import CircleFeedScreen from '../screens/CircleFeedScreen';
import CircleSettingsScreen from '../screens/CircleSettingsScreen';
import CreateCirclePostScreen from '../screens/CreateCirclePostScreen';
import { COLORS } from '../styles/theme';

const Tab = createBottomTabNavigator();
const HomeStack = createNativeStackNavigator();
const SearchStack = createNativeStackNavigator();
const ProfileStack = createNativeStackNavigator();
const CirclesStack = createNativeStackNavigator();

function HomeStackNavigator({ onCreatePost, onLogout }) {
    return (
        <HomeStack.Navigator screenOptions={{ headerShown: false }}>
            <HomeStack.Screen name="HomeMain">
                {(props) => (
                    <HomeScreen
                        {...props}
                        onCreatePost={onCreatePost}
                        onLogout={onLogout}
                    />
                )}
            </HomeStack.Screen>
            <HomeStack.Screen name="UserProfile" component={UserProfileScreen} />
            <HomeStack.Screen name="PastQuotes" component={PastQuotesScreen} />
        </HomeStack.Navigator>
    );
}

function SearchStackNavigator() {
    return (
        <SearchStack.Navigator screenOptions={{ headerShown: false }}>
            <SearchStack.Screen name="Search" component={SearchScreen} />
            <SearchStack.Screen name="UserProfile" component={UserProfileScreen} />
        </SearchStack.Navigator>
    );
}

function ProfileStackNavigator({ onLogout }) {
    return (
        <ProfileStack.Navigator screenOptions={{ headerShown: false }}>
            <ProfileStack.Screen name="ProfileMain">
                {(props) => <ProfileScreen {...props} onLogout={onLogout} />}
            </ProfileStack.Screen>
            <ProfileStack.Screen name="UserProfile" component={UserProfileScreen} />
        </ProfileStack.Navigator>
    );
}

function CirclesStackNavigator() {
    return (
        <CirclesStack.Navigator
            screenOptions={{
                headerStyle: { backgroundColor: COLORS.card },
                headerTintColor: COLORS.text,
                headerTitleStyle: { fontWeight: '600' },
            }}
        >
            <CirclesStack.Screen
                name="CirclesList"
                component={CirclesListScreen}
                options={{ headerTitle: 'Circles' }}
            />
            <CirclesStack.Screen
                name="CircleDetail"
                component={CircleFeedScreen}
                options={({ route }) => ({
                    headerTitle: route.params?.circleName || 'Circle',
                    headerBackTitle: 'Back',
                })}
            />
            <CirclesStack.Screen
                name="CircleSettings"
                component={CircleSettingsScreen}
                options={{
                    headerTitle: 'Circle Settings',
                    headerBackTitle: 'Back',
                }}
            />
            <CirclesStack.Screen
                name="CreateCirclePost"
                component={CreateCirclePostScreen}
                options={{
                    headerShown: false,
                    presentation: 'modal',
                }}
            />
            <CirclesStack.Screen
                name="UserProfile"
                component={UserProfileScreen}
                options={{ headerShown: false }}
            />
        </CirclesStack.Navigator>
    );
}

export default function AppNavigator({ onCreatePost, onLogout }) {
    return (
        <Tab.Navigator
            screenOptions={{
                headerShown: false,
                tabBarShowLabel: false,
                tabBarActiveTintColor: COLORS.primary,
                tabBarInactiveTintColor: COLORS.textLight,
                tabBarStyle: {
                    backgroundColor: COLORS.card,
                    borderTopColor: COLORS.border,
                    paddingBottom: 5,
                    paddingTop: 5,
                    height: 60,
                },
            }}
        >
            <Tab.Screen
                name="HomeTab"
                options={{
                    tabBarIcon: ({ color, size }) => (
                        <Ionicons name="home" size={size} color={color} />
                    ),
                    tabBarLabel: 'Home',
                }}
            >
                {() => (
                    <HomeStackNavigator
                        onCreatePost={onCreatePost}
                        onLogout={onLogout}
                    />
                )}
            </Tab.Screen>
            <Tab.Screen
                name="SearchTab"
                options={{
                    tabBarIcon: ({ color, size }) => (
                        <Ionicons name="search" size={size} color={color} />
                    ),
                    tabBarLabel: 'Search',
                }}
            >
                {() => <SearchStackNavigator />}
            </Tab.Screen>
            <Tab.Screen
                name="CirclesTab"
                options={{
                    tabBarIcon: ({ color, size }) => (
                        <Ionicons name="people" size={size} color={color} />
                    ),
                    tabBarLabel: 'Circles',
                }}
            >
                {() => <CirclesStackNavigator />}
            </Tab.Screen>
            <Tab.Screen
                name="ProfileTab"
                options={{
                    tabBarIcon: ({ color, size }) => (
                        <Ionicons name="person" size={size} color={color} />
                    ),
                    tabBarLabel: 'Profile',
                }}
            >
                {() => <ProfileStackNavigator onLogout={onLogout} />}
            </Tab.Screen>
        </Tab.Navigator>
    );
}
