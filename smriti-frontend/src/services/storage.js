import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEY_PREFIX } from '../constants/config';

const STORAGE_KEY = STORAGE_KEY_PREFIX;

/**
 * Get all users from AsyncStorage
 * @returns {Promise<Array>} - Array of user objects
 */
export const getAllUsers = async () => {
    try {
        const jsonValue = await AsyncStorage.getItem(`${STORAGE_KEY}:users`);
        return jsonValue != null ? JSON.parse(jsonValue) : [];
    } catch (e) {
        console.error('Error reading users:', e);
        return [];
    }
};

/**
 * Save a new user to AsyncStorage
 * @param {Object} user - User object with id, username, password, createdAt
 * @returns {Promise<boolean>} - Success status
 */
export const saveUser = async (user) => {
    try {
        const users = await getAllUsers();
        users.push(user);
        const jsonValue = JSON.stringify(users);
        await AsyncStorage.setItem(`${STORAGE_KEY}:users`, jsonValue);
        return true;
    } catch (e) {
        console.error('Error saving user:', e);
        return false;
    }
};

/**
 * Get user by username
 * @param {string} username - Username to search for
 * @returns {Promise<Object|null>} - User object or null
 */
export const getUserByUsername = async (username) => {
    try {
        const users = await getAllUsers();
        return users.find(u => u.username.toLowerCase() === username.toLowerCase()) || null;
    } catch (e) {
        console.error('Error getting user:', e);
        return null;
    }
};

/**
 * Clear all data (for development)
 * @returns {Promise<boolean>}
 */
export const clearAllData = async () => {
    try {
        await AsyncStorage.clear();
        return true;
    } catch (e) {
        console.error('Error clearing data:', e);
        return false;
    }
};

/**
 * Save a new post
 * @param {Object} post 
 */
export const savePost = async (post) => {
    try {
        const posts = await getPosts();
        // Add ID if missing
        const newPost = { ...post, id: Date.now().toString() };
        const updatedPosts = [newPost, ...posts];
        await AsyncStorage.setItem(`${STORAGE_KEY}:posts`, JSON.stringify(updatedPosts));
        return true;
    } catch (e) {
        console.error('Error saving post:', e);
        return false;
    }
};

/**
 * Get all posts
 */
export const getPosts = async () => {
    try {
        const jsonValue = await AsyncStorage.getItem(`${STORAGE_KEY}:posts`);
        return jsonValue != null ? JSON.parse(jsonValue) : [];
    } catch (e) {
        console.error('Error reading posts:', e);
        return [];
    }
};
