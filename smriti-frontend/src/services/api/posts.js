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

/**
 * Create a post in a specific circle
 * @param {Object} postData - Post data including circleId
 * @param {string} postData.circleId - Circle ID to post to
 * @param {string} [postData.title] - Post title
 * @param {string} [postData.textContent] - Post text content
 * @param {Object} [postData.image] - Image object from ImagePicker
 * @param {Object} [postData.document] - Document object from DocumentPicker
 * @returns {Promise<Object>} - {success, post, error}
 */
export const createCirclePost = async (postData) => {
  try {
    const formData = new FormData();

    // Determine content_type based on attachments
    let contentType = 'note';
    if (postData.document) {
      contentType = 'document';
    } else if (postData.image) {
      contentType = 'image';
    }
    formData.append('content_type', contentType);

    // Add visibility and circle_ids for circle posts
    formData.append('visibility', 'circles');
    formData.append('circle_ids', postData.circleId);

    // Add text content
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
      error: error.message || 'Failed to create circle post'
    };
  }
};

/**
 * Search posts with full-text search and filters
 * @param {Object} params - Search parameters
 * @param {string} [params.q] - Search query text
 * @param {string} [params.author_id] - Filter by author user ID
 * @param {string} [params.content_type] - Filter by content type
 * @param {string} [params.start_date] - Filter from date (ISO)
 * @param {string} [params.end_date] - Filter until date (ISO)
 * @param {number} [params.skip] - Pagination offset
 * @param {number} [params.limit] - Pagination limit
 * @returns {Promise<Object>} - {success, data: {posts, total, skip, limit}, error}
 */
export const searchPosts = async (params = {}) => {
  try {
    const cleanParams = {};
    if (params.q) cleanParams.q = params.q;
    if (params.author_id) cleanParams.author_id = params.author_id;
    if (params.content_type) cleanParams.content_type = params.content_type;
    if (params.start_date) cleanParams.start_date = params.start_date;
    if (params.end_date) cleanParams.end_date = params.end_date;
    if (params.skip !== undefined) cleanParams.skip = params.skip;
    if (params.limit !== undefined) cleanParams.limit = params.limit;

    return await apiGet('/api/posts/search', cleanParams);
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to search posts'
    };
  }
};
