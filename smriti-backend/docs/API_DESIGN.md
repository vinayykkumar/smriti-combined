# API Design: Sign Up

This document outlines the API contract for the user registration (Sign Up) flow.

## 1. Sign Up Endpoint

**Goal:** Create a new user account.

-   **URL:** `/api/v1/auth/signup`
-   **Method:** `POST`
-   **Content-Type:** `application/json`

### Request Body
What the App sends to the Server:

```json
{
  "username": "kalyan",
  "password": "yourSecretPassword123"
}
```

-   **username** (string, required): Unique identifier for the user. Min 3 chars.
-   **password** (string, required): The raw password (the server will hash it). Min 6 chars.

### Success Response
**Status Code:** `201 Created`

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "userId": "user_123456789",
    "username": "kalyan",
    "token": "eyJhbGciOiJIUzI1NiIsIn..."
  }
}
```

-   **token**: This is a **JWT (JSON Web Token)**. The app should save this (in AsyncStorage) and send it with future requests (like "Create Post") to prove who the user is.

### Error Responses

**1. Username already exists**
**Status Code:** `409 Conflict`
```json
{
  "success": false,
  "error": "Username is already taken"
}
```

**2. Invalid Input (e.g., password too short)**
**Status Code:** `400 Bad Request`
```json
{
  "success": false,
  "error": "Password must be at least 6 characters long"
}
```

**3. Server Error**
**Status Code:** `500 Internal Server Error`
```json
{
  "success": false,
  "error": "Something went wrong on the server. Please try again."
}
```
