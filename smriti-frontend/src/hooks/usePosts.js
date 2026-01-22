import { useState, useEffect, useCallback } from 'react';
import { fetchPosts as fetchPostsApi } from '../services/api';

/**
 * Custom hook for managing posts
 * @returns {object} Posts state and methods
 */
export function usePosts() {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [refreshing, setRefreshing] = useState(false);

    const loadPosts = useCallback(async (skip = 0, limit = 20) => {
        try {
            setLoading(true);
            setError(null);
            const loadedPosts = await fetchPostsApi(skip, limit);
            setPosts(loadedPosts);
        } catch (err) {
            setError(err.message || 'Failed to load posts');
            console.error('Error loading posts:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const refreshPosts = useCallback(async () => {
        try {
            setRefreshing(true);
            setError(null);
            const loadedPosts = await fetchPostsApi();
            setPosts(loadedPosts);
        } catch (err) {
            setError(err.message || 'Failed to refresh posts');
            console.error('Error refreshing posts:', err);
        } finally {
            setRefreshing(false);
        }
    }, []);

    const addPost = useCallback((newPost) => {
        setPosts(prevPosts => [newPost, ...prevPosts]);
    }, []);

    useEffect(() => {
        loadPosts();
    }, [loadPosts]);

    return {
        posts,
        loading,
        error,
        refreshing,
        loadPosts,
        refreshPosts,
        addPost,
    };
}
