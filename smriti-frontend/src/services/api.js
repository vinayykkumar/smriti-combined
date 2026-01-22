import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL, STORAGE_KEY_USER_TOKEN } from '../constants/config';
import { getApiHeaders, handleApiResponse, buildQueryString } from '../utils/apiHelpers';
import { handleApiError, getErrorMessage } from '../utils/errorHandler';
import { getData } from '../utils/storageHelpers';

/**
 * Get the auth token from AsyncStorage
 * @returns {Promise<string|null>} - Auth token or null
 */
export const getAuthToken = async () => {
    try {
        // Use storage helper for consistency
        const token = await getData(STORAGE_KEY_USER_TOKEN);
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

        const headers = getApiHeaders(token);
        // Remove Content-Type for FormData - React Native sets it automatically
        delete headers['Content-Type'];
        
        const response = await fetch(`${API_BASE_URL}/posts/`, {
            method: 'POST',
            headers,
            body: formData
        });

        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorInfo = handleApiError({ response, data: errorData });
            return {
                success: false,
                error: getErrorMessage(errorInfo)
            };
        }

        const data = await handleApiResponse(response);
        console.log('Response data:', JSON.stringify(data, null, 2));
        return data;
    } catch (error) {
        const errorInfo = handleApiError(error);
        console.error('Error creating post:', errorInfo.message);
        return {
            success: false,
            error: getErrorMessage(errorInfo)
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

        const queryParams = buildQueryString({ skip, limit });
        const response = await fetch(`${API_BASE_URL}/posts/${queryParams}`, {
            method: 'GET',
            headers: getApiHeaders(token)
        });

        if (!response.ok) {
            console.error('Failed to fetch posts:', response.status);
            return [];
        }

        const responseData = await handleApiResponse(response);
        console.log('Fetched posts:', responseData);

        // Extract posts from response.data.posts
        return responseData.data?.posts || [];
    } catch (error) {
        const errorInfo = handleApiError(error);
        console.error('Error fetching posts:', errorInfo.message);
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
            headers: getApiHeaders(token)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorInfo = handleApiError({ response, data: errorData });
            return {
                success: false,
                error: getErrorMessage(errorInfo)
            };
        }

        const data = await handleApiResponse(response);
        console.log('Fetched user profile:', data);
        return data;
    } catch (error) {
        const errorInfo = handleApiError(error);
        console.error('Error fetching user profile:', errorInfo.message);
        return {
            success: false,
            error: getErrorMessage(errorInfo)
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

        const queryParams = buildQueryString({ skip, limit });
        const response = await fetch(
            `${API_BASE_URL}/posts/me${queryParams}`,
            {
                method: 'GET',
                headers: getApiHeaders(token)
            }
        );

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorInfo = handleApiError({ response, data: errorData });
            return {
                success: false,
                error: getErrorMessage(errorInfo)
            };
        }

        const data = await handleApiResponse(response);
        console.log('Fetched my posts:', data);
        return data;
    } catch (error) {
        const errorInfo = handleApiError(error);
        console.error('Error fetching my posts:', errorInfo.message);
        return {
            success: false,
            error: getErrorMessage(errorInfo)
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
            headers: getApiHeaders(token)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorInfo = handleApiError({ response, data: errorData });
            return {
                success: false,
                error: getErrorMessage(errorInfo)
            };
        }

        const data = await handleApiResponse(response);
        console.log('Delete post response:', data);
        return data;
    } catch (error) {
        const errorInfo = handleApiError(error);
        console.error('Error deleting post:', errorInfo.message);
        return {
            success: false,
            error: getErrorMessage(errorInfo)
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
            headers: getApiHeaders(authToken),
            body: JSON.stringify({
                token,
                platform
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorInfo = handleApiError({ response, data: errorData });
            return {
                success: false,
                error: getErrorMessage(errorInfo)
            };
        }

        const data = await handleApiResponse(response);
        console.log('Register token response:', data);
        return data;
    } catch (error) {
        const errorInfo = handleApiError(error);
        console.error('Error registering notification token:', errorInfo.message);
        return {
            success: false,
            error: getErrorMessage(errorInfo)
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
            headers: getApiHeaders(authToken),
            body: JSON.stringify({
                token,
                platform
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorInfo = handleApiError({ response, data: errorData });
            return {
                success: false,
                error: getErrorMessage(errorInfo)
            };
        }

        const data = await handleApiResponse(response);
        console.log('Unregister token response:', data);
        return data;
    } catch (error) {
        const errorInfo = handleApiError(error);
        console.error('Error unregistering notification token:', errorInfo.message);
        return {
            success: false,
            error: getErrorMessage(errorInfo)
        };
    }
};

