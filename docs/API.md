# API Documentation

## Base URL

- **Production**: `https://smriti-backend-r293.onrender.com`
- **Local**: `http://localhost:8000`

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Health

- `GET /health` - Health check
- `GET /health/db` - Database health check

### Authentication

- `POST /api/auth/signup` - Create new user
- `POST /api/auth/login` - Login with username/email
- `GET /api/auth/me` - Get current user

### Posts

- `GET /api/posts` - Get all posts
- `POST /api/posts` - Create new post
- `GET /api/posts/{id}` - Get post by ID
- `PUT /api/posts/{id}` - Update post
- `DELETE /api/posts/{id}` - Delete post

### Users

- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile

## Response Format

All responses follow this format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

## Error Format

```json
{
  "success": false,
  "error": "Error message",
  "details": { ... }
}
```
