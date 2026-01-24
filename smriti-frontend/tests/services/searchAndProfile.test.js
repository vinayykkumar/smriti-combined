/**
 * Tests for search and user profile API service functions.
 */

// Mock the client module
jest.mock('../../src/services/api/client', () => ({
    apiGet: jest.fn(),
    apiPost: jest.fn(),
    apiDelete: jest.fn(),
}));

const { apiGet } = require('../../src/services/api/client');
const { searchPosts } = require('../../src/services/api/posts');
const { fetchUserProfileById, fetchUserPosts } = require('../../src/services/api/users');

describe('Search API', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('should call searchPosts with text query', async () => {
        const mockResponse = {
            success: true,
            data: {
                posts: [{ postId: '1', title: 'Test Post' }],
                total: 1,
                skip: 0,
                limit: 20,
            },
        };
        apiGet.mockResolvedValue(mockResponse);

        const result = await searchPosts({ q: 'test' });

        expect(apiGet).toHaveBeenCalledWith('/api/posts/search', { q: 'test' });
        expect(result.data.posts).toHaveLength(1);
        expect(result.data.total).toBe(1);
    });

    it('should call searchPosts with all filters', async () => {
        apiGet.mockResolvedValue({ success: true, data: { posts: [], total: 0 } });

        await searchPosts({
            q: 'test',
            author_id: '507f1f77bcf86cd799439011',
            content_type: 'note',
            start_date: '2024-01-01',
            end_date: '2024-12-31',
            skip: 0,
            limit: 20,
        });

        expect(apiGet).toHaveBeenCalledWith('/api/posts/search', {
            q: 'test',
            author_id: '507f1f77bcf86cd799439011',
            content_type: 'note',
            start_date: '2024-01-01',
            end_date: '2024-12-31',
            skip: 0,
            limit: 20,
        });
    });

    it('should omit undefined params from search', async () => {
        apiGet.mockResolvedValue({ success: true, data: { posts: [], total: 0 } });

        await searchPosts({ q: 'test' });

        const calledParams = apiGet.mock.calls[0][1];
        expect(calledParams.author_id).toBeUndefined();
        expect(calledParams.content_type).toBeUndefined();
        expect(calledParams.start_date).toBeUndefined();
        expect(calledParams.end_date).toBeUndefined();
    });

    it('should handle search errors gracefully', async () => {
        apiGet.mockRejectedValue(new Error('Network error'));

        const result = await searchPosts({ q: 'test' });

        expect(result.success).toBe(false);
        expect(result.error).toBe('Network error');
    });
});

describe('User Profile API', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('should fetch user profile by ID', async () => {
        const mockResponse = {
            success: true,
            data: {
                user: {
                    id: '507f1f77bcf86cd799439011',
                    username: 'testuser',
                    post_count: 5,
                    joined_at: '2024-01-01T00:00:00Z',
                },
            },
        };
        apiGet.mockResolvedValue(mockResponse);

        const result = await fetchUserProfileById('507f1f77bcf86cd799439011');

        expect(apiGet).toHaveBeenCalledWith('/api/users/507f1f77bcf86cd799439011');
        expect(result.data.user.username).toBe('testuser');
        expect(result.data.user.post_count).toBe(5);
    });

    it('should fetch user posts with pagination', async () => {
        const mockResponse = {
            success: true,
            data: {
                posts: [{ postId: '1', title: 'Post 1' }, { postId: '2', title: 'Post 2' }],
                total: 10,
                skip: 0,
                limit: 20,
            },
        };
        apiGet.mockResolvedValue(mockResponse);

        const result = await fetchUserPosts('507f1f77bcf86cd799439011', 0, 20);

        expect(apiGet).toHaveBeenCalledWith('/api/users/507f1f77bcf86cd799439011/posts', { skip: 0, limit: 20 });
        expect(result.data.posts).toHaveLength(2);
        expect(result.data.total).toBe(10);
    });

    it('should handle profile fetch errors gracefully', async () => {
        apiGet.mockRejectedValue(new Error('User not found'));

        const result = await fetchUserProfileById('invalid-id');

        expect(result.success).toBe(false);
        expect(result.error).toBe('User not found');
    });

    it('should handle user posts fetch errors gracefully', async () => {
        apiGet.mockRejectedValue(new Error('Server error'));

        const result = await fetchUserPosts('507f1f77bcf86cd799439011');

        expect(result.success).toBe(false);
        expect(result.error).toBe('Server error');
    });
});
