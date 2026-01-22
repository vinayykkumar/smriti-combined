Smriti 🌳
Sanskrit: स्मृति (Memory/Reflection)

A minimal, non-addictive reflection portal designed for a small group of spiritually inclined users. Smriti serves as a digital satsanga tree - a shared reflective space for collective memory and learning.

📖 Table of Contents
Project Philosophy
Features
Architecture
Technology Stack
Project Structure
Getting Started
API Documentation
Deployment
Contributing
License
🕉️ Project Philosophy
Core Principles
Minimal by Design

No likes, comments, shares, or algorithms
Chronological display of posts only
Content focused on learnings, not opinions
Non-Addictive

No notifications
No infinite scroll
No engagement metrics
No background refresh
Small Trusted Community

Initially designed for 5 users
Private, shared reflective space
Focus on quality over quantity
What Smriti Is
✅ A shared reflective space
✅ A digital satsanga tree 🌳
✅ A collective memory store

What Smriti Is NOT
❌ Not a social network
❌ Not a teaching platform
❌ Not a content marketing tool

✨ Features
Current Features (v1.0)
User Authentication

Simple username/password authentication
JWT-based session management
Secure password hashing with bcrypt
Reflection Management

Create reflections with multiple content types:
Personal notes
External links (Instagram, web)
Document uploads (PDF, DOC)
View all reflections chronologically
See author name and date (no time)
Content Types

Notes: Personal written reflections
Links: Share meaningful external content
Documents: Upload and share PDFs or documents
Future Enhancements (Planned)
Edit post within 10 minutes of creation
Role-based access (admin)
Daily post limit (to encourage restraint)
Read-only mode for silent days
🏗️ Architecture
┌───────────────────────────────────────┐
│     Mobile Layer (React Native)       │
│                                       │
│  • Auth Screen                        │
│  • Home Screen (All Reflections)     │
│  • Post Screen (Create Reflection)   │
└───────────────────────────────────────┘
                 ↓ ↑
          HTTPS REST API
                 ↓ ↑
┌───────────────────────────────────────┐
│    Backend Layer (Node.js/Express)    │
│                                       │
│  Deployed: Render.com                 │
│  URL: smriti-api.onrender.com         │
│                                       │
│  Routes:                              │
│  • POST /api/auth/signup              │
│  • POST /api/auth/login               │
│  • GET  /api/posts                    │
│  • POST /api/posts                    │
└───────────────────────────────────────┘
                 ↓ ↑
          Database Queries
                 ↓ ↑
┌───────────────────────────────────────┐
│   Database Layer (MongoDB Atlas)      │
│                                       │
│  Collections:                         │
│  • users                              │
│  • posts                              │
└───────────────────────────────────────┘
🛠️ Technology Stack
Frontend (Mobile)
Framework: React Native
Language: JavaScript
Navigation: React Navigation
State Management: React Context API
Platform: Android (APK)
Backend (API)
Runtime: Node.js v18+
Framework: Express.js
Authentication: JWT (jsonwebtoken)
Security: helmet, cors, bcrypt
Validation: express-validator
File Upload: Multer + Cloudinary
Database
Database: MongoDB Atlas (Free Tier)
ODM: Mongoose
Storage: 512MB (more than enough for 5 users)
Deployment & Services
Backend Hosting: Render.com (Free Tier)
Database: MongoDB Atlas (Free Tier)
File Storage: Cloudinary (Free Tier - 25GB)
Total Monthly Cost: ₹0 (FREE) 🎉

📂 Project Structure
smriti/
│
├── mobile/                          # React Native Frontend
│   ├── android/                     # Android build files
│   ├── src/
│   │   ├── screens/
│   │   │   ├── AuthScreen.js       # Sign up/Sign in
│   │   │   ├── HomeScreen.js       # View reflections
│   │   │   └── PostScreen.js       # Create reflection
│   │   ├── components/
│   │   │   ├── PostCard.js         # Reflection card component
│   │   │   └── Header.js           # App header
│   │   ├── services/
│   │   │   └── api.js              # API service layer
│   │   ├── navigation/
│   │   │   └── AppNavigator.js     # Navigation setup
│   │   ├── context/
│   │   │   └── AuthContext.js      # Authentication state
│   │   └── config.js               # Configuration (API URL)
│   ├── App.js
│   └── package.json
│
├── backend/                         # Node.js + Express API
│   ├── src/
│   │   ├── models/
│   │   │   ├── User.js             # User schema
│   │   │   └── Post.js             # Post schema
│   │   ├── routes/
│   │   │   ├── auth.js             # Authentication routes
│   │   │   └── posts.js            # Post CRUD routes
│   │   ├── middleware/
│   │   │   ├── auth.js             # JWT verification
│   │   │   ├── errorHandler.js     # Error handling
│   │   │   └── upload.js           # File upload handling
│   │   ├── config/
│   │   │   ├── db.js               # MongoDB connection
│   │   │   └── cloudinary.js       # Cloudinary config
│   │   └── utils/
│   │       ├── generateToken.js    # JWT generation
│   │       └── validators.js       # Request validators
│   ├── server.js                    # Main entry point
│   ├── package.json
│   ├── .env.example                 # Environment template
│   └── README.md
│
├── docs/                            # Documentation
│   ├── PROJECT_OVERVIEW.md         # Detailed project context
│   ├── API_DOCUMENTATION.md        # API reference
│   ├── DEPLOYMENT_GUIDE.md         # Deployment steps
│   ├── DATABASE_SCHEMA.md          # Schema documentation
│   └── FRONTEND_GUIDE.md           # React Native guide
│
├── .gitignore
├── README.md                        # This file
└── LICENSE
🚀 Getting Started
Prerequisites
Node.js v18 or higher
npm or yarn
MongoDB Atlas account (free)
Cloudinary account (free, for file uploads)
React Native CLI (for mobile development)
Android Studio (for building APK)
Backend Setup
Clone the repository

git clone <repository-url>
cd smriti
Install backend dependencies

cd backend
npm install
Configure environment variables

cp .env.example .env
Edit .env with your credentials:

PORT=5000
NODE_ENV=development
MONGODB_URI=mongodb+srv://your_username:password@cluster.mongodb.net/smriti
JWT_SECRET=your_very_secret_key_here
JWT_EXPIRE=30d
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
Start the development server

npm run dev
Backend will run on http://localhost:5000

Mobile Setup (React Native)
Install mobile dependencies

cd mobile
npm install
Configure API URL

Edit src/config.js:

const API_URL = __DEV__ 
  ? 'http://localhost:5000'              // Local development
  : 'https://smriti-api.onrender.com'    // Production
Run on Android

npx react-native run-android
Build APK for distribution

cd android
./gradlew assembleRelease
APK will be in android/app/build/outputs/apk/release/

📚 API Documentation
Base URL
Local: http://localhost:5000
Production: https://smriti-api.onrender.com

Authentication Endpoints
Sign Up
POST /api/auth/signup
Content-Type: application/json

{
  "username": "satsangi",
  "password": "secret123"
}

Response: 200 OK
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "_id": "507f1f77bcf86cd799439011",
    "username": "satsangi",
    "createdAt": "2026-01-04T10:00:00.000Z"
  }
}
Login
POST /api/auth/login
Content-Type: application/json

{
  "username": "satsangi",
  "password": "secret123"
}

Response: 200 OK
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { ... }
}
Get Current User
GET /api/auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "user": { ... }
}
Post Endpoints
Get All Posts
GET /api/posts
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "count": 10,
  "posts": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "contentType": "note",
      "textContent": "Today I learned about stillness...",
      "author": {
        "username": "satsangi",
        "userId": "507f191e810c19729de860ea"
      },
      "createdAt": "2026-01-04T10:00:00.000Z"
    }
  ]
}
Create Post
POST /api/posts
Authorization: Bearer <token>
Content-Type: application/json

{
  "contentType": "note",
  "title": "On Meditation",
  "textContent": "Today I experienced deep calm..."
}

Response: 201 Created
{
  "success": true,
  "post": { ... }
}
For complete API documentation, see docs/API_DOCUMENTATION.md

🚢 Deployment
Backend Deployment (Render)
Create Render account at render.com

Create new Web Service

Connect GitHub repository
Build Command: cd backend && npm install
Start Command: cd backend && npm start
Set environment variables in Render dashboard:

MONGODB_URI
JWT_SECRET
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
Deploy - Render will auto-deploy on every git push

MongoDB Atlas Setup
Create free cluster at mongodb.com/cloud/atlas
Create database user
Whitelist IP: 0.0.0.0/0 (allow all)
Get connection string
Add to environment variables
APK Distribution
For 5 users, simply:

Build release APK
Share via Google Drive / WhatsApp
Users enable "Install from Unknown Sources"
Install directly
No Play Store needed!

For detailed deployment steps, see docs/DEPLOYMENT_GUIDE.md

🤝 Contributing
This is a private project for a small spiritual community.

If you're part of the community and want to contribute:

Follow the minimal design philosophy
Test thoroughly before submitting
Update documentation
Keep it simple
📄 License
This project is private and intended for personal use by a small spiritual community.

🙏 Credits
"This is seva through tech"

Built with mindfulness for the journey of self-reflection.

📞 Support
For issues or questions, please contact the project maintainer.

📖 Additional Documentation
Project Overview - Philosophy and detailed context
API Documentation - Complete API reference
Database Schema - MongoDB schema details
Deployment Guide - Step-by-step deployment
Frontend Guide - React Native implementation
Version: 1.0.0
Last Updated: January 4, 2026

May this space serve the path of reflection 🌳