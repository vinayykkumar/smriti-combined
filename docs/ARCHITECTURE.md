# Smriti Architecture

## Overview

Smriti follows a monorepo architecture with clear separation between backend and frontend.

## System Architecture

```
┌─────────────────┐
│   Mobile App    │
│  (React Native) │
└────────┬────────┘
         │
         │ HTTPS/REST API
         │
┌────────▼────────┐
│   FastAPI       │
│   Backend       │
└────────┬────────┘
         │
    ┌────┴────┐
    │        │
┌───▼───┐ ┌──▼────┐
│MongoDB│ │Cloudinary│
│ Atlas │ │  (Files) │
└───────┘ └─────────┘
```

## Backend Architecture

### Layer Structure

1. **Router Layer** (`app/*/router.py`)
   - Handles HTTP requests
   - Request validation
   - Response formatting

2. **Service Layer** (`app/*/service.py`)
   - Business logic
   - Data transformation
   - Error handling

3. **Repository Layer** (`app/*/repository.py`)
   - Database operations
   - Data access abstraction

4. **Schema Layer** (`app/*/schemas.py`)
   - Pydantic models
   - Data validation

## Frontend Architecture

### Component Structure

- **Screens**: Top-level page components
- **Components**: Reusable UI components
- **Services**: API and external service integrations
- **Contexts**: Global state management
- **Hooks**: Custom React hooks
- **Utils**: Utility functions

## Data Flow

1. User interacts with mobile app
2. Frontend calls API service
3. API service makes HTTP request to backend
4. Backend processes request through layers
5. Response flows back through layers
6. Frontend updates UI

## Security

- JWT tokens for authentication
- Password hashing with bcrypt
- CORS protection
- Environment variable management
