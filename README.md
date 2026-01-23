# Smriti 🌳

> **स्मृति** (Sanskrit: Memory/Reflection)

A minimal, non-addictive reflection portal designed for a small spiritual community. This monorepo contains both the backend API and mobile frontend application. new

---

## 📖 Table of Contents

- [About](#about)
- [Monorepo Structure](#monorepo-structure)
- [Getting Started](#getting-started)
- [Development](#development)
- [Project Philosophy](#project-philosophy)
- [Contributing](#contributing)
- [License](#license)

---

## 🕉️ About

Smriti is a **digital satsanga tree** - a shared reflective space for collective memory and learning. The platform embodies these core principles:

- **Minimal by Design**: No likes, comments, shares, or algorithms
- **Non-Addictive**: No notifications, infinite scroll, or engagement metrics
- **Small Trusted Community**: Initially designed for a small spiritual community
- **Chronological Only**: Simple time-based reflection display

---

## 📂 Monorepo Structure

```
smriti-combined/
├── smriti-backend/          # FastAPI backend (Python)
│   ├── app/                 # Application code
│   ├── tests/               # Test suite
│   ├── docs/                # Backend documentation
│   ├── pyproject.toml       # Poetry dependencies
│   └── README.md            # Backend-specific docs
│
├── smriti-frontend/         # React Native mobile app (Expo)
│   ├── src/                 # Application code
│   ├── assets/              # Images and static assets
│   ├── docs/                # Frontend documentation
│   ├── package.json         # NPM dependencies
│   └── README.md            # Frontend-specific docs (if exists)
│
├── README.md                # This file
├── .gitignore               # Git ignore rules
├── LICENSE                  # Project license
└── CONTRIBUTING.md          # Contribution guidelines
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.10+ and pip
- **MongoDB Atlas** account (free tier)
- **Cloudinary** account (free tier, for file uploads)
- **Expo CLI** (for mobile development)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smriti-combined.git
   cd smriti-combined
   ```

2. **Set up the Backend**
   ```bash
   cd smriti-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   # Copy .env.example to .env and configure
   uvicorn app.main:app --reload
   ```

3. **Set up the Frontend**
   ```bash
   cd smriti-frontend
   npm install
   # Configure environment variables
   npm start
   ```

For detailed setup instructions, see:
- [Backend README](./smriti-backend/README.md)
- Frontend documentation (in `smriti-frontend/docs/`)

---

## 💻 Development

### Backend Development

```bash
cd smriti-backend
# Activate virtual environment
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API Documentation: `http://localhost:8000/docs`

### Frontend Development

```bash
cd smriti-frontend
npm start
# Follow Expo CLI prompts
```

### Running Tests

**Backend:**
```bash
cd smriti-backend
pytest
```

**Frontend:**
```bash
cd smriti-frontend
npm test  # If test suite exists
```

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB Atlas
- **Authentication**: JWT
- **File Storage**: Cloudinary
- **Deployment**: Render.com

### Frontend
- **Framework**: React Native with Expo
- **Navigation**: React Navigation
- **State Management**: React Hooks
- **Push Notifications**: Firebase Cloud Messaging

---

## 🕉️ Project Philosophy

This project embodies a **minimal, non-addictive** philosophy:

### What We Built
✅ Simple authentication  
✅ Chronological post retrieval  
✅ Basic CRUD operations  
✅ Secure file storage  

### What We Deliberately Excluded
❌ No likes, reactions, or engagement metrics  
❌ No comments or threads  
❌ No recommendation algorithms  
❌ No analytics or tracking  
❌ No infinite scroll pagination  
❌ No follower/following system  

> "This is seva through tech" - Built with mindfulness for the journey of self-reflection.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact the project maintainer

---

**Version**: 1.0.0  
**Last Updated**: January 2026

May this space serve the path of reflection 🌳
