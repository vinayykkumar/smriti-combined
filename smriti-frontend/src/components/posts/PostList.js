import React from 'react';
import { FlatList, RefreshControl } from 'react-native';
import { COLORS } from '../../styles/theme';
import PostCard from './PostCard';

/**
 * PostList Component - Displays a list of posts
 * @param {array} posts - Array of post objects
 * @param {function} onRefresh - Refresh handler
 * @param {boolean} refreshing - Refreshing state
 * @param {ReactNode} ListHeaderComponent - Optional header component
 */
export default function PostList({
    posts,
    onRefresh,
    refreshing = false,
    ListHeaderComponent,
    contentContainerStyle
}) {
    const renderPostItem = ({ item }) => <PostCard post={item} />;

    return (
        <FlatList
            data={posts}
            renderItem={renderPostItem}
            keyExtractor={(item) => item.postId || item.id || item.date}
            ListHeaderComponent={ListHeaderComponent}
            contentContainerStyle={contentContainerStyle}
            refreshControl={
                <RefreshControl
                    refreshing={refreshing}
                    onRefresh={onRefresh}
                    tintColor={COLORS.primary}
                />
            }
        />
    );
}
