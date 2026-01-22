# Profile Page API Documentation

## Overview
This document covers the new API endpoints for the profile page feature, including user statistics and personalized post feed.

**Base URL:** `https://smriti-backend-r293.onrender.com/api`

---

## New Endpoints

### 1. Get User Profile with Stats
Get the current user's profile information including statistics.

**Endpoint:** `GET /users/me`

**Authentication:** Required (Bearer Token)

**Request Headers:**
```http
Authorization: Bearer <your_jwt_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "status": "success",
  "data": {
    "user": {
      "id": "6966399edd0b7914eafbe0ac",
      "username": "johndoe",
      "display_name": "John Doe",
      "email": "john@example.com",
      "phone": null,
      "joined_at": "2026-01-13T12:25:02.030000",
      "post_count": 5
    }
  }
}
```

**Response Fields:**
- `id` (string): User's unique identifier
- `username` (string): User's username
- `display_name` (string): User's display name
- `email` (string): User's email address
- `phone` (string|null): User's phone number
- `joined_at` (datetime): Account creation timestamp
- `post_count` (integer): Total number of posts by the user

---

### 2. Get User's Posts (Profile Feed)
Get all posts created by the current authenticated user.

**Endpoint:** `GET /posts/me`

**Authentication:** Required (Bearer Token)

**Query Parameters:**
- `skip` (integer, optional): Number of posts to skip (default: 0)
- `limit` (integer, optional): Maximum posts to return (default: 20, max: 100)

**Request Example:**
```http
GET /posts/me?skip=0&limit=20
Authorization: Bearer <your_jwt_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "status": "success",
  "results": 2,
  "data": {
    "posts": [
      {
        "postId": "69663a20dd0b7914eafbe0ad",
        "contentType": "note",
        "title": "My First Post",
        "textContent": "This is my first post!",
        "linkUrl": null,
        "imageUrl": null,
        "documentUrl": null,
        "author": {
          "userId": "6966399edd0b7914eafbe0ac",
          "username": "johndoe"
        },
        "createdAt": "2026-01-13T12:30:00.000000"
      },
      {
        "postId": "69663b30dd0b7914eafbe0ae",
        "contentType": "image",
        "title": "Sunset Photo",
        "textContent": "Beautiful sunset today",
        "imageUrl": "https://res.cloudinary.com/...",
        "author": {
          "userId": "6966399edd0b7914eafbe0ac",
          "username": "johndoe"
        },
        "createdAt": "2026-01-13T13:00:00.000000"
      }
    ]
  }
}
```

**Response Fields:**
- `results` (integer): Number of posts returned
- `posts` (array): Array of post objects (same format as GET /posts/)

---

### 3. Delete Post (Enhanced)
Delete a post (author only). Now properly validates ownership.

**Endpoint:** `DELETE /posts/{postId}`

**Authentication:** Required (Bearer Token)

**Request Example:**
```http
DELETE /posts/69663a20dd0b7914eafbe0ad
Authorization: Bearer <your_jwt_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Post deleted successfully"
}
```

**Error Response (403 Forbidden):**
```json
{
  "success": false,
  "error": "Not authorized to delete this post"
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Post not found"
}
```

---

## Frontend Integration Guide

### React Native Example

#### 1. Fetch User Profile
```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

const fetchUserProfile = async () => {
  try {
    const token = await AsyncStorage.getItem('authToken');
    
    const response = await fetch('https://smriti-backend-r293.onrender.com/api/users/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    const data = await response.json();
    
    if (data.success) {
      const user = data.data.user;
      console.log('Username:', user.username);
      console.log('Post Count:', user.post_count);
      console.log('Joined:', new Date(user.joined_at).toLocaleDateString());
      return user;
    }
  } catch (error) {
    console.error('Error fetching profile:', error);
  }
};
```

#### 2. Fetch User's Posts
```typescript
const fetchUserPosts = async (skip = 0, limit = 20) => {
  try {
    const token = await AsyncStorage.getItem('authToken');
    
    const response = await fetch(
      `https://smriti-backend-r293.onrender.com/api/posts/me?skip=${skip}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Total posts:', data.results);
      return data.data.posts;
    }
  } catch (error) {
    console.error('Error fetching posts:', error);
  }
};
```

#### 3. Delete Post
```typescript
const deletePost = async (postId: string) => {
  try {
    const token = await AsyncStorage.getItem('authToken');
    
    const response = await fetch(
      `https://smriti-backend-r293.onrender.com/api/posts/${postId}`,
      {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Post deleted successfully');
      // Refresh the posts list
      await fetchUserPosts();
      // Refresh user profile to update post_count
      await fetchUserProfile();
    } else {
      console.error('Delete failed:', data.error);
    }
  } catch (error) {
    console.error('Error deleting post:', error);
  }
};
```

#### 4. Complete Profile Screen Component
```typescript
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, Alert } from 'react-native';

const ProfileScreen = () => {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfileData();
  }, []);

  const loadProfileData = async () => {
    setLoading(true);
    const userData = await fetchUserProfile();
    const userPosts = await fetchUserPosts();
    
    setUser(userData);
    setPosts(userPosts);
    setLoading(false);
  };

  const handleDeletePost = async (postId: string) => {
    Alert.alert(
      'Delete Post',
      'Are you sure you want to delete this post?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            await deletePost(postId);
            await loadProfileData(); // Refresh data
          },
        },
      ]
    );
  };

  if (loading) {
    return <Text>Loading...</Text>;
  }

  return (
    <View>
      {/* Profile Header */}
      <View>
        <Text style={{ fontSize: 24 }}>@{user?.username}</Text>
        <Text>{user?.display_name}</Text>
        <Text>Joined: {new Date(user?.joined_at).toLocaleDateString()}</Text>
        <Text>{user?.post_count} Posts</Text>
      </View>

      {/* Posts List */}
      <FlatList
        data={posts}
        keyExtractor={(item) => item.postId}
        renderItem={({ item }) => (
          <View>
            <Text>{item.title}</Text>
            <Text>{item.textContent}</Text>
            <TouchableOpacity onPress={() => handleDeletePost(item.postId)}>
              <Text style={{ color: 'red' }}>Delete</Text>
            </TouchableOpacity>
          </View>
        )}
      />
    </View>
  );
};
```

---

## Important Notes

### Authentication
- All endpoints require a valid JWT token in the Authorization header
- Token format: `Bearer <token>`
- Token is returned from `/auth/login` and `/auth/signup` endpoints

### Pagination
- Use `skip` and `limit` parameters for pagination
- Default: `skip=0`, `limit=20`
- Maximum limit: 100 posts per request

### Post Count Updates
- `post_count` automatically updates when posts are created or deleted
- Always fetch fresh user profile after creating/deleting posts to get updated count

### Error Handling
- Always check `success` field in response
- Handle 401 (Unauthorized) - token expired or invalid
- Handle 403 (Forbidden) - trying to delete someone else's post
- Handle 404 (Not Found) - post doesn't exist

### Date Formatting
- All timestamps are in ISO 8601 format
- Use JavaScript `Date` object or libraries like `date-fns` for formatting

---

## Testing with Postman

The updated Postman collection includes:
- **Users** → Get User Profile (with Stats)
- **Posts** → Get My Posts (Profile Feed)
- **Posts** → Delete Post

Import the collection from: `Smriti_API.postman_collection.json`

---

## Changelog

### v1.1.0 (2026-01-13)
- ✅ Added `GET /users/me` - User profile with stats
- ✅ Added `GET /posts/me` - User's personalized post feed
- ✅ Enhanced `DELETE /posts/{id}` - Ownership validation
- ✅ Added `post_count` field to user profile
- ✅ Added `joined_at` field to user profile
- ✅ Changed post ID field from `postId` to `id` in responses (backwards compatible)

---

## Support

For questions or issues:
- Check the API documentation at: `/docs` (Swagger UI)
- Review existing endpoints in Postman collection
- Contact backend team for assistance
