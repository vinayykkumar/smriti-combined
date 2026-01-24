/**
 * Tests for SearchScreen component.
 */
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Animated } from 'react-native';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
    getItem: jest.fn(() => Promise.resolve(null)),
    setItem: jest.fn(() => Promise.resolve()),
    removeItem: jest.fn(() => Promise.resolve()),
}));

// Mock the search API
jest.mock('../../src/services/api/posts', () => ({
    searchPosts: jest.fn(() => Promise.resolve({
        success: true,
        data: { posts: [], total: 0, skip: 0, limit: 20 },
    })),
}));

// Mock Ionicons
jest.mock('@expo/vector-icons', () => ({
    Ionicons: () => 'Ionicons',
}));

const SearchScreen = require('../../src/screens/SearchScreen').default;

const mockNavigation = {
    navigate: jest.fn(),
};

const mockRoute = {
    params: {},
};

describe('SearchScreen', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders search input', () => {
        const { getByPlaceholderText } = render(
            <SearchScreen navigation={mockNavigation} route={mockRoute} />
        );
        expect(getByPlaceholderText('Search reflections...')).toBeTruthy();
    });

    it('renders header title', () => {
        const { getByText } = render(
            <SearchScreen navigation={mockNavigation} route={mockRoute} />
        );
        expect(getByText('Search')).toBeTruthy();
    });

    it('renders empty state when no search', () => {
        const { getByText } = render(
            <SearchScreen navigation={mockNavigation} route={mockRoute} />
        );
        expect(getByText('Search Reflections')).toBeTruthy();
    });

    it('renders filters toggle', () => {
        const { getByText } = render(
            <SearchScreen navigation={mockNavigation} route={mockRoute} />
        );
        expect(getByText('Filters')).toBeTruthy();
    });

    it('handles text input correctly', () => {
        const { getByPlaceholderText, getByDisplayValue } = render(
            <SearchScreen navigation={mockNavigation} route={mockRoute} />
        );
        const input = getByPlaceholderText('Search reflections...');
        fireEvent.changeText(input, 'test query');
        expect(getByDisplayValue('test query')).toBeTruthy();
    });

    it('shows active filter state when author is set via route params', () => {
        const routeWithAuthor = {
            params: {
                authorId: '507f1f77bcf86cd799439011',
                authorName: 'testuser',
            },
        };
        const { getByText } = render(
            <SearchScreen navigation={mockNavigation} route={routeWithAuthor} />
        );
        expect(getByText('Filters (active)')).toBeTruthy();
    });
});
