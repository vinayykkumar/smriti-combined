# Smriti Backend API 🌳

> **स्मृति** (Sanskrit: Memory/Reflection)

RESTful API backend for **Smriti** - a minimal, non-addictive reflection portal designed for a small spiritual community. This API serves as the backend for the Smriti mobile application (React Native).

---

## 📖 Table of Contents

- [About](#about)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
  - [Running Locally](#running-locally)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Posts/Reflections](#postsreflections)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Security Features](#security-features)
- [Philosophy & Design Principles](#philosophy--design-principles)

---

## 🕉️ About

Smriti is a **digital satsanga tree** - a shared reflective space for collective memory and learning. The backend provides a secure, minimal API that embodies these core principles:

- **Minimal by Design**: No likes, comments, shares, or algorithms
- **Non-Addictive**: No notifications, infinite scroll, or engagement metrics
- **Small Trusted Community**: Initially designed for 5 users
- **Chronological Only**: Simple time-based reflection display

### What This Backend Provides

✅ JWT-based authentication  
✅ Reflection posting (notes, links, documents)  
✅ Chronological post retrieval  
✅ File upload handling via Cloudinary  
✅ Secure password hashing  

---

## 🛠️ Technology Stack

| Category | Technology |
|----------|-----------|
| **Language** | Python 3.10+ |
| **Framework** | FastAPI |
| **Database** | MongoDB Atlas (Free Tier) |
| **ODM** | Motor (async MongoDB driver) |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | passlib with bcrypt |
| **Security** | FastAPI CORS middleware |
| **Validation** | Pydantic (built-in with FastAPI) |
| **File Upload** | python-multipart + Cloudinary |
| **Server** | Uvicorn (ASGI server) |
| **Hosting** | Render.com (Free Tier) |

**Total Monthly Cost**: ₹0 (FREE) 🎉

---

## 📂 Project Structure

```
smriti-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User Pydantic models & DB schema
│   │   └── post.py              # Post Pydantic models & DB schema
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   └── posts.py             # Post CRUD endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings & environment variables
│   │   ├── security.py          # JWT & password hashing utilities
│   │   └── database.py          # MongoDB connection
│   └── dependencies/
│       ├── __init__.py
│       └── auth.py              # JWT verification dependency
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── .gitignore
└── README.md                     # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.10 or higher
- **pip** (Python package manager)
- **MongoDB Atlas** account (free tier)
- **Cloudinary** account (free tier, for file uploads)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/smriti-backend.git
cd smriti-backend
```

2. **Create a virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

### Environment Configuration

1. **Copy the example environment file**

```bash
cp .env.example .env
```

2. **Edit `.env` with your credentials**

```env
# Server Configuration
PORT=8000
ENVIRONMENT=development

# Database
MONGODB_URI=mongodb+srv://your_username:password@cluster.mongodb.net/smriti?retryWrites=true&w=majority

# JWT Configuration
SECRET_KEY=your_very_secret_key_here_minimum_32_characters_long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Cloudinary (for file uploads)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

> **Security Note**: Never commit `.env` to version control. Use a strong, random value for `SECRET_KEY` (generate with `openssl rand -hex 32`).

### Running Locally

**Development mode (with auto-reload)**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

**Interactive API Documentation** will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📚 API Documentation

### Base URL

- **Local**: `http://localhost:8000`
- **Production**: `https://smriti-api.onrender.com`

> **Note**: FastAPI automatically generates interactive API documentation:
> - Swagger UI: Visit `/docs` for interactive API testing
> - ReDoc: Visit `/redoc` for clean API documentation

---

### Authentication

#### 1. Sign Up

**Endpoint**: `POST /api/auth/signup`

**Request Body**:
```json
{
  "username": "satsangi",
  "password": "secret123"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "_id": "507f1f77bcf86cd799439011",
    "username": "satsangi",
    "createdAt": "2026-01-04T10:00:00.000Z"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Username already exists or validation error
- `500 Server Error`: Internal server error

---

#### 2. Login

**Endpoint**: `POST /api/auth/login`

**Request Body**:
```json
{
  "username": "satsangi",
  "password": "secret123"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "_id": "507f1f77bcf86cd799439011",
    "username": "satsangi",
    "createdAt": "2026-01-04T10:00:00.000Z"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `400 Bad Request`: Validation error

---

#### 3. Get Current User

**Endpoint**: `GET /api/auth/me`

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "user": {
    "_id": "507f1f77bcf86cd799439011",
    "username": "satsangi",
    "createdAt": "2026-01-04T10:00:00.000Z"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired token

---

### Posts/Reflections

#### 1. Get All Posts

**Endpoint**: `GET /api/posts`

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters** (optional):
- `limit`: Number of posts to return (default: 50)
- `skip`: Number of posts to skip for pagination

**Response** (200 OK):
```json
{
  "success": true,
  "count": 10,
  "posts": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "contentType": "note",
      "title": "On Meditation",
      "textContent": "Today I learned about stillness...",
      "author": {
        "username": "satsangi",
        "userId": "507f191e810c19729de860ea"
      },
      "createdAt": "2026-01-04T10:00:00.000Z",
      "updatedAt": "2026-01-04T10:00:00.000Z"
    }
  ]
}
```

**Posts are returned in chronological order (newest first)**

---

#### 2. Create Post

**Endpoint**: `POST /api/posts`

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body** (for text note):
```json
{
  "contentType": "note",
  "title": "On Meditation",
  "textContent": "Today I experienced deep calm during morning meditation..."
}
```

**Request Body** (for link):
```json
{
  "contentType": "link",
  "title": "Beautiful Teaching",
  "linkUrl": "https://example.com/teaching",
  "textContent": "Optional description of the link"
}
```

**Request Body** (for document upload):
```
Content-Type: multipart/form-data

Fields:
- contentType: "document"
- title: "Sacred Text"
- document: <file> (PDF, DOC, DOCX)
- textContent: "Optional description"
```

**Response** (201 Created):
```json
{
  "success": true,
  "post": {
    "_id": "507f1f77bcf86cd799439011",
    "contentType": "note",
    "title": "On Meditation",
    "textContent": "Today I experienced...",
    "author": {
      "username": "satsangi",
      "userId": "507f191e810c19729de860ea"
    },
    "createdAt": "2026-01-04T10:00:00.000Z"
  }
}
```

**Content Types**:
- `note`: Personal written reflections
- `link`: External links (web, Instagram, etc.)
- `document`: File uploads (PDF, DOC, DOCX)

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `400 Bad Request`: Validation error or invalid content type
- `413 Payload Too Large`: File size exceeds limit (10MB)

---

## 🗄️ Database Schema

### User Model (Pydantic Schema)

```python
from pydantic import BaseModel, Field
from datetime import datetime

class User(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)  # Hashed before storing
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Post Model (Pydantic Schema)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class ContentType(str, Enum):
    note = "note"
    link = "link"
    document = "document"

class Post(BaseModel):
    author: dict = Field(..., description="Author info with userId and username")
    content_type: ContentType
    title: Optional[str] = None
    text_content: Optional[str] = None
    link_url: Optional[str] = None         # For link posts
    document_url: Optional[str] = None     # For document posts (Cloudinary)
    document_type: Optional[str] = None    # File type (pdf, doc, docx)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
```

---

## 🚢 Deployment

### Deploy to Render.com (Free Tier)

1. **Create Render account** at [render.com](https://render.com)

2. **Create new Web Service**
   - Connect your GitHub repository
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: `Python 3`

3. **Set Environment Variables** in Render Dashboard:
   ```
   ENVIRONMENT=production
   MONGODB_URI=<your-mongodb-atlas-uri>
   SECRET_KEY=<your-strong-secret-key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=43200
   CLOUDINARY_CLOUD_NAME=<your-cloudinary-name>
   CLOUDINARY_API_KEY=<your-cloudinary-key>
   CLOUDINARY_API_SECRET=<your-cloudinary-secret>
   ```

4. **Deploy** - Render will auto-deploy on every `git push` to main branch

### MongoDB Atlas Setup

1. Create free cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create database user with password
3. **Network Access**: Add IP `0.0.0.0/0` (allow from anywhere)
4. Get connection string from "Connect" → "Connect your application"
5. Replace `<password>` and database name in connection string
6. Add to `MONGODB_URI` environment variable

### Cloudinary Setup

1. Create free account at [cloudinary.com](https://cloudinary.com)
2. Get credentials from Dashboard:
   - Cloud name
   - API Key
   - API Secret
3. Add to environment variables

---

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt rounds (10)
- **JWT Authentication**: Secure token-based auth with expiration
- **CORS Protection**: Configured for mobile app origins
- **Helmet.js**: Security headers protection
- **Input Validation**: express-validator for request sanitization
- **Environment Variables**: Sensitive data not hardcoded
- **HTTPS**: Enforced on production (via Render)

---

## 🕉️ Philosophy & Design Principles

This backend embodies the **minimal, non-addictive** philosophy:

### What We Built
✅ Simple authentication (username/password only)  
✅ Chronological post retrieval (no sorting algorithms)  
✅ Basic CRUD operations  
✅ Secure file storage  

### What We Deliberately Excluded
❌ No likes, reactions, or engagement metrics  
❌ No comments or threads  
❌ No notifications system  
❌ No recommendation algorithms  
❌ No analytics or tracking  
❌ No infinite scroll pagination  
❌ No follower/following system  

> "This is seva through tech" - Built with mindfulness for the journey of self-reflection.

---

## 📞 Support

For issues or questions related to the Smriti backend, please contact the project maintainer or open an issue on GitHub.

---

## 📄 License

This project is private and intended for personal use by a small spiritual community.

---

**Version**: 1.0.0  
**Last Updated**: January 4, 2026

May this space serve the path of reflection 🌳
