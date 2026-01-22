# Backend Requirements for Smriti App (Phase 2)

This document outlines the API changes required in `smriti-backend` to support the new **Profile** and **Post Management** features in the frontend.

## 1. My Posts (Profile Feed)
**Goal:** Display a list of posts created *only* by the logged-in user.

### New Endpoint: `GET /posts/me`
*   **Description:** Fetch all posts authored by the current authenticated user.
*   **Auth:** Required (Bearer Token).
*   **Query Params:**
    *   `skip`: (Integer) For pagination.
    *   `limit`: (Integer) Default 20.
*   **Response:**
    ```json
    {
      "status": "success",
      "results": 5,
      "data": {
        "posts": [ ... ] // Array of post objects
      }
    }
    ```

## 2. Delete Post
**Goal:** Allow users to delete their own posts.

### New Endpoint: `DELETE /posts/{postId}`
*   **Description:** Delete a specific post.
*   **Auth:** Required (Bearer Token).
*   **Critical Logic:**
    *   **Ownership Check:** The backend **MUST** verify that `post.author_id` matches the `current_user.id`.
    *   If user is NOT the author, return `403 Forbidden`.
    *   If post not found, return `404 Not Found`.
*   **Response:**
    ```json
    {
      "status": "success",
      "message": "Post deleted successfully"
    }
    ```

## 3. User Profile Stats (Optional but Recommended)
**Goal:** Show user details on the profile screen (e.g., "Joined Jan 2024", "Total Reflections: 12").

### New Endpoint: `GET /users/me`
*   **Description:** Get details of the current user.
*   **Auth:** Required.
*   **Response:**
    ```json
    {
      "status": "success",
      "data": {
        "user": {
          "id": "...",
          "username": "vinay",
          "email": "...",
          "joined_at": "2024-01-12T...",
          "post_count": 12
        }
      }
    }
    ```

## 4. Edit Post (Future Preparation)
**Goal:** Allow correcting typos.

### New Endpoint: `PATCH /posts/{postId}`
*   **Description:** Update title or content of a post.
*   **Auth:** Required + Ownership Check.
*   **Body:**
    ```json
    {
      "title": "New Title",
      "content": "Updated content..."
    }
    ```

---
**Action Items for Backend Developer:**
1.  Implement `GET /posts/me`.
2.  Implement `DELETE /posts/{id}` with strict ownership validation.
3.  Deploy updated API to Render.