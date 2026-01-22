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

## 5. Image Upload Support (NEW - Phase 2.1)
**Goal:** Allow users to attach images to their reflections/posts.

### Updated Endpoint: `POST /posts/`
*   **Description:** Create a new post with optional image attachment.
*   **Auth:** Required (Bearer Token).
*   **Content-Type:** `multipart/form-data` (changed from `application/x-www-form-urlencoded`)
*   **Form Fields:**
    *   `content_type`: (String) "note"
    *   `title`: (String) Post title
    *   `text_content`: (String) Post description/content
    *   `image`: (File, Optional) Image file (JPEG, PNG, WebP)
*   **Image Storage:**
    *   **Recommended:** Use **Cloudinary** (already in use)
    *   Upload image to Cloudinary
    *   Store returned URL in database
*   **Validation:**
    *   Max file size: 5MB
    *   Allowed types: JPEG, PNG, WebP
    *   Return 400 Bad Request if validation fails
*   **Response:**
    ```json
    {
      "success": true,
      "post": {
        "id": "...",
        "title": "...",
        "textContent": "...",
        "imageUrl": "https://res.cloudinary.com/...",  // NEW FIELD
        "author": { ... },
        "createdAt": "..."
      }
    }
    ```

### Updated Endpoint: `GET /posts/` and `GET /posts/me`
*   **Description:** Include `imageUrl` field in post responses.
*   **Response Changes:**
    *   Add `image_url` field to each post object
    *   Field should be `null` if no image attached
*   **Example:**
    ```json
    {
      "status": "success",
      "results": 2,
      "data": {
        "posts": [
          {
            "id": "...",
            "title": "...",
            "text_content": "...",
            "image_url": "https://res.cloudinary.com/...",  // NEW
            "author": { ... },
            "created_at": "..."
          },
          {
            "id": "...",
            "title": "...",
            "text_content": "...",
            "image_url": null,  // No image for this post
            "author": { ... },
            "created_at": "..."
          }
        ]
      }
    }
    ```

### Database Schema Update
*   **Table:** `posts`
*   **New Column:** `image_url` (String, nullable)
*   **Migration Required:** Yes

---
**Action Items for Backend Developer:**
1.  Implement `GET /posts/me`.
2.  Implement `DELETE /posts/{id}` with strict ownership validation.
3.  **[NEW]** Update `POST /posts/` to accept `multipart/form-data` with optional image file.
4.  **[NEW]** Integrate Cloudinary for image storage and retrieval.
5.  **[NEW]** Add `image_url` column to `posts` table (nullable).
6.  **[NEW]** Update `GET /posts/` and `GET /posts/me` to include `image_url` in responses.
7.  Deploy updated API to Render.