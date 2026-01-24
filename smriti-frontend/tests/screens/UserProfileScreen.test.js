/**
 * Tests for UserProfileScreen component.
 */
import React from 'react';
import { render, waitFor } from '@testing-library/react-native';

// Mock user API
const mockFetchUserProfileById = jest.fn(() => Promise.resolve({
    success: true,
    data: {
        user: {
            id: '507f1f77bcf86cd799439011',
            username: 'testuser',
            display_name: 'Test User',
            post_count: 3,
            joined_at: '2024-06-15T00:00:00Z',
        },
    },
}));

const mockFetchUserPosts = jest.fn(() => Promise.resolve({
    success: true,
    data: {
        posts: [
            {
                postId: '1',
                title: 'First Post',
                text_content: 'Content of first post',
                author: { user_id: '507f1f77bcf86cd799439011', username: 'testuser' },
                content_type: 'note',
                created_at: '2024-06-20T00:00:00Z',
            },
        ],
        total: 1,
        skip: 0,
        limit: 20,
    },
}));

jest.mock('../../src/services/api/users', () => ({
    fetchUserProfileById: (...args) => mockFetchUserProfileById(...args),
    fetchUserPosts: (...args) => mockFetchUserPosts(...args),
}));

// Mock Ionicons
jest.mock('@expo/vector-icons', () => ({
    Ionicons: () => 'Ionicons',
}));

const UserProfileScreen = require('../../src/screens/UserProfileScreen').default;

const mockNavigation = {
    navigate: jest.fn(),
    push: jest.fn(),
    goBack: jest.fn(),
};

const mockRoute = {
    params: {
        userId: '507f1f77bcf86cd799439011',
        username: 'testuser',
    },
};

describe('UserProfileScreen', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('calls fetch APIs on mount', async () => {
        render(
            <UserProfileScreen navigation={mockNavigation} route={mockRoute} />
        );

        await waitFor(() => {
            expect(mockFetchUserProfileById).toHaveBeenCalledWith('507f1f77bcf86cd799439011');
            expect(mockFetchUserPosts).toHaveBeenCalledWith('507f1f77bcf86cd799439011', 0, 20);
        });
    });

    it('renders loading state initially with username', () => {
        const { getAllByText } = render(
            <UserProfileScreen navigation={mockNavigation} route={mockRoute} />
        );
        expect(getAllByText('@testuser').length).toBeGreaterThan(0);
    });

    it('renders user profile after loading', async () => {
        const { getAllByText } = render(
            <UserProfileScreen navigation={mockNavigation} route={mockRoute} />
        );

        await waitFor(() => {
            expect(getAllByText('@testuser').length).toBeGreaterThan(0);
        });
    });

    it('displays post count after loading', async () => {
        const { getByText } = render(
            <UserProfileScreen navigation={mockNavigation} route={mockRoute} />
        );

        await waitFor(() => {
            expect(getByText('3')).toBeTruthy();
        });
    });

    it('shows search by author button', async () => {
        const { getByText } = render(
            <UserProfileScreen navigation={mockNavigation} route={mockRoute} />
        );

        await waitFor(() => {
            expect(getByText('Search posts by this author')).toBeTruthy();
        });
    });

    it('renders posts after loading', async () => {
        const { getByText } = render(
            <UserProfileScreen navigation={mockNavigation} route={mockRoute} />
        );

        await waitFor(() => {
            expect(getByText('First Post')).toBeTruthy();
        });
    });
});
