import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL, STORAGE_KEY_USER_TOKEN } from '../constants/config';

/**
 * Get the auth token from AsyncStorage
 * @returns {Promise<string|null>} - Auth token or null
 */
export const getAuthToken = async () => {
    try {
        const token = await AsyncStorage.getItem(STORAGE_KEY_USER_TOKEN);
        return token;
    } catch (error) {
        console.error('Error getting auth token:', error);
        return null;
    }
};

/**
 * Create a new post via API
 * @param {Object} postData - {title (optional), textContent (optional), image (optional), document (optional)}
 * @returns {Promise<Object>} - {success, post, error}
 */
export const createPost = async (postData) => {
    try {
        const token = await getAuthToken();
        if (!token) {
            return { success: false, error: 'No authentication token found' };
        }

        console.log('Creating post with token:', token ? 'Token exists' : 'No token');
        console.log('Post data:', {
            hasTitle: !!postData.title,
            hasText: !!postData.textContent,
            hasImage: !!postData.image,
            hasDocument: !!postData.document
        });

        // Create FormData for multipart upload
        const formData = new FormData();

        // Determine content_type based on attachments (priority: document > image > note)
        let contentType = 'note';
        if (postData.document) {
            contentType = 'document';
        } else if (postData.image) {
            contentType = 'image';
        }
        formData.append('content_type', contentType);

        // Add title and text_content only if provided
        if (postData.title) {
            formData.append('title', postData.title);
        }
        if (postData.textContent) {
            formData.append('text_content', postData.textContent);
        }

        // Add image if provided
        if (postData.image) {
            const imageUri = postData.image.uri;
            const filename = imageUri.split('/').pop();
            const match = /\.(\w+)$/.exec(filename);
            const type = match ? `image/${match[1]}` : 'image/jpeg';

            formData.append('image', {
                uri: imageUri,
                name: filename,
                type: type
            });
            console.log('Image attached:', filename, type);
        }

        // Add document if provided
        if (postData.document) {
            const doc = postData.document;
            formData.append('document', {
                uri: doc.uri,
                name: doc.name,
                type: doc.mimeType || 'application/pdf'
            });
            console.log('Document attached:', doc.name, doc.mimeType);
        }

        const response = await fetch(`${API_BASE_URL}/posts/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                // Note: Don't set Content-Type header for FormData
                // React Native will set it automatically with boundary
            },
            body: formData
        });

        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', JSON.stringify(data, null, 2));

        if (!response.ok) {
            return {
                success: false,
                error: data.message || data.error || `Server error: ${response.status}`
            };
        }

        return data;
    } catch (error) {
        console.error('Error creating post:', error);
        return {
            success: false,
            error: error.message || 'Network error occurred'
        };
    }
};

/**
 * Fetch all posts from API
 * @param {number} skip - Number of posts to skip (for pagination)
 * @param {number} limit - Maximum number of posts to fetch
 * @returns {Promise<Array>} - Array of posts
 */
export const fetchPosts = async (skip = 0, limit = 20) => {
    try {
        const token = await getAuthToken();
        if (!token) {
            console.error('No authentication token found');
            return [];
        }

        const response = await fetch(`${API_BASE_URL}/posts/?skip=${skip}&limit=${limit}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            console.error('Failed to fetch posts:', response.status);
            return [];
        }

        const responseData = await response.json();
        console.log('Fetched posts:', responseData);

        // Extract posts from response.data.posts
        return responseData.data?.posts || [];
    } catch (error) {
        console.error('Error fetching posts:', error);
        return [];
    }
};

/**
 * Fetch current user's profile with stats
 * @returns {Promise<Object>} - {success, data: {user: {...}}}
 */
export const fetchUserProfile = async () => {
    try {
        const token = await getAuthToken();
        if (!token) {
            return { success: false, error: 'No authentication token found' };
        }

        const response = await fetch(`${API_BASE_URL}/users/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        console.log('Fetched user profile:', data);

        if (!response.ok) {
            return {
                success: false,
                error: data.error || `Server error: ${response.status}`
            };
        }

        return data;
    } catch (error) {
        console.error('Error fetching user profile:', error);
        return {
            success: false,
            error: error.message || 'Network error occurred'
        };
    }
};

/**
 * Fetch user's own posts
 * @param {number} skip - Number of posts to skip (for pagination)
 * @param {number} limit - Maximum number of posts to fetch
 * @returns {Promise<Object>} - {success, results, data: {posts: [...]}}
 */
export const fetchMyPosts = async (skip = 0, limit = 20) => {
    try {
        const token = await getAuthToken();
        if (!token) {
            return { success: false, error: 'No authentication token found' };
        }

        const response = await fetch(
            `${API_BASE_URL}/posts/me?skip=${skip}&limit=${limit}`,
            {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );

        const data = await response.json();
        console.log('Fetched my posts:', data);

        if (!response.ok) {
            return {
                success: false,
                error: data.error || `Server error: ${response.status}`
            };
        }

        return data;
    } catch (error) {
        console.error('Error fetching my posts:', error);
        return {
            success: false,
            error: error.message || 'Network error occurred'
        };
    }
};

/**
 * Delete a post (ownership validated by backend)
 * @param {string} postId - Post ID to delete
 * @returns {Promise<Object>} - {success, message}
 */
export const deletePost = async (postId) => {
    try {
        const token = await getAuthToken();
        if (!token) {
            return { success: false, error: 'No authentication token found' };
        }

        const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        console.log('Delete post response:', data);

        if (!response.ok) {
            return {
                success: false,
                error: data.error || `Server error: ${response.status}`
            };
        }

        return data;
    } catch (error) {
        console.error('Error deleting post:', error);
        return {
            success: false,
            error: error.message || 'Network error occurred'
        };
    }
};

/**
 * Register device token for push notifications
 * @param {string} token - FCM device token
 * @param {string} platform - 'ios' or 'android'
 * @returns {Promise<Object>} - {success, message}
 */
export const registerNotificationToken = async (token, platform) => {
    try {
        const authToken = await getAuthToken();
        if (!authToken) {
            return { success: false, error: 'No authentication token found' };
        }

        const response = await fetch(`${API_BASE_URL}/notifications/register-token`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token,
                platform
            })
        });

        const data = await response.json();
        console.log('Register token response:', data);

        if (!response.ok) {
            return {
                success: false,
                error: data.error || `Server error: ${response.status}`
            };
        }

        return data;
    } catch (error) {
        console.error('Error registering notification token:', error);
        return {
            success: false,
            error: error.message || 'Network error occurred'
        };
    }
};

/**
 * Unregister device token from push notifications
 * @param {string} token - FCM device token
 * @param {string} platform - 'ios' or 'android'
 * @returns {Promise<Object>} - {success, message}
 */
export const unregisterNotificationToken = async (token, platform) => {
    try {
        const authToken = await getAuthToken();
        if (!authToken) {
            return { success: false, error: 'No authentication token found' };
        }

        const response = await fetch(`${API_BASE_URL}/notifications/unregister-token`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token,
                platform
            })
        });

        const data = await response.json();
        console.log('Unregister token response:', data);

        if (!response.ok) {
            return {
                success: false,
                error: data.error || `Server error: ${response.status}`
            };
        }

        return data;
    } catch (error) {
        console.error('Error unregistering notification token:', error);
        return {
            success: false,
            error: error.message || 'Network error occurred'
        };
    }
};

