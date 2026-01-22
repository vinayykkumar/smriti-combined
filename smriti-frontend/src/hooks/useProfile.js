import { useState, useEffect, useCallback } from 'react';
import { fetchUserProfile, fetchMyPosts, deletePost } from '../services/api';

/**
 * Custom hook for managing user profile and posts
 * @returns {object} Profile state and methods
 */
export function useProfile() {
    const [user, setUser] = useState(null);
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState(null);

    const loadProfile = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch profile and posts in parallel
            const [profileData, postsData] = await Promise.all([
                fetchUserProfile(),
                fetchMyPosts()
            ]);

            if (profileData.success) {
                setUser(profileData.data.user);
            } else {
                setError(profileData.error);
            }

            if (postsData.success) {
                setPosts(postsData.data.posts);
            } else {
                setError(postsData.error);
            }
        } catch (err) {
            setError(err.message || 'Failed to load profile');
            console.error('Error loading profile:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const refreshProfile = useCallback(async () => {
        try {
            setRefreshing(true);
            setError(null);

            const [profileData, postsData] = await Promise.all([
                fetchUserProfile(),
                fetchMyPosts()
            ]);

            if (profileData.success) {
                setUser(profileData.data.user);
            }

            if (postsData.success) {
                setPosts(postsData.data.posts);
            }
        } catch (err) {
            setError(err.message || 'Failed to refresh profile');
            console.error('Error refreshing profile:', err);
        } finally {
            setRefreshing(false);
        }
    }, []);

    const removePost = useCallback(async (postId) => {
        const result = await deletePost(postId);

        if (result.success) {
            // Optimistically remove from UI
            setPosts(prev => prev.filter(p => p.postId !== postId));
            // Update post count
            setUser(prev => prev ? { ...prev, post_count: prev.post_count - 1 } : null);
            return { success: true };
        }

        return result;
    }, []);

    useEffect(() => {
        loadProfile();
    }, [loadProfile]);

    return {
        user,
        posts,
        loading,
        refreshing,
        error,
        refreshProfile,
        removePost
    };
}
