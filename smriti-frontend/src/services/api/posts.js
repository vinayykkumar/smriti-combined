/**
 * Posts API service.
 */
import { apiGet, apiPost, apiDelete } from './client';

/**
 * Fetch all posts
 * @param {number} skip - Number of posts to skip
 * @param {number} limit - Maximum number of posts to fetch
 * @returns {Promise<Array>} - Array of posts
 */
export const fetchPosts = async (skip = 0, limit = 20) => {
  try {
    const response = await apiGet('/api/posts', { skip, limit });
    return response.data?.posts || [];
  } catch (error) {
    console.error('Error fetching posts:', error.message);
    return [];
  }
};

/**
 * Create a new post
 * @param {Object} postData - {title, textContent, image, document, contentType}
 * @returns {Promise<Object>} - {success, post, error}
 */
export const createPost = async (postData) => {
  try {
    // Create FormData for multipart upload
    const formData = new FormData();

    // Determine content_type based on attachments (priority: document > image > note)
    let contentType = postData.contentType || 'note';
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
    if (postData.linkUrl) {
      formData.append('link_url', postData.linkUrl);
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
    }

    // Add document if provided
    if (postData.document) {
      const doc = postData.document;
      formData.append('document', {
        uri: doc.uri,
        name: doc.name,
        type: doc.mimeType || 'application/pdf'
      });
    }

    return await apiPost('/api/posts/', formData);
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to create post'
    };
  }
};

/**
 * Fetch user's own posts
 * @param {number} skip - Number of posts to skip
 * @param {number} limit - Maximum number of posts to fetch
 * @returns {Promise<Object>} - {success, data: {posts: [...]}, error}
 */
export const fetchMyPosts = async (skip = 0, limit = 20) => {
  try {
    return await apiGet('/api/posts/me', { skip, limit });
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to fetch posts'
    };
  }
};

/**
 * Delete a post
 * @param {string} postId - Post ID to delete
 * @returns {Promise<Object>} - {success, message, error}
 */
export const deletePost = async (postId) => {
  try {
    return await apiDelete(`/api/posts/${postId}`);
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to delete post'
    };
  }
};
