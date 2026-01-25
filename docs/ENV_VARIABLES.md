# Environment Variables

## Required Environment Variables

These environment variables must be set before running the application in production.

### Backend (`smriti-backend/.env`)

```bash
# =============================================================================
# REQUIRED - Application will not start without these
# =============================================================================

# Environment mode: "development", "staging", or "production"
ENVIRONMENT=production

# MongoDB connection string
# Replace with your MongoDB Atlas or self-hosted MongoDB URI
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority

# Database name
DATABASE_NAME=smriti_production

# JWT secret key for authentication
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=<generate-a-64-character-hex-string>

# =============================================================================
# TODAY'S QUOTE FEATURE - Required for quote functionality
# =============================================================================

# Cron job authentication secret
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
# Used to authenticate POST /api/internal/daily-quote-init and daily-quote-push
CRON_SECRET=<generate-a-64-character-hex-string>

# =============================================================================
# PUSH NOTIFICATIONS - Required for notifications
# =============================================================================

# Firebase Admin SDK credentials (JSON file path or inline JSON)
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json
# OR provide inline JSON:
# FIREBASE_CREDENTIALS={"type":"service_account","project_id":"..."}

# =============================================================================
# OPTIONAL - Have sensible defaults
# =============================================================================

# Server configuration
HOST=0.0.0.0
PORT=8000

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:19006

# Logging level
LOG_LEVEL=INFO
```

### Frontend (`smriti-frontend/.env` or app.config.js)

```bash
# =============================================================================
# API CONFIGURATION
# =============================================================================

# Backend API URL
# Development: http://localhost:8000
# Production: https://api.yourapp.com
API_BASE_URL=https://api.yourapp.com

# =============================================================================
# FIREBASE (for push notifications)
# =============================================================================

# These are typically configured in app.json or google-services.json
# Not stored as env variables in React Native
```

---

## How to Generate Secrets

### Using Python (recommended)
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Using OpenSSL
```bash
openssl rand -hex 32
```

### Using Node.js
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

---

## Cron Job Configuration

The Today's Quote feature requires two cron jobs to be configured:

### 1. Daily Quote Initialization
- **Endpoint**: `POST /api/internal/daily-quote-init`
- **Schedule**: Every hour (e.g., `0 * * * *`)
- **Header**: `X-Cron-Secret: <your-CRON_SECRET>`

Example cURL:
```bash
curl -X POST https://api.yourapp.com/api/internal/daily-quote-init \
  -H "X-Cron-Secret: your-cron-secret-here"
```

### 2. Daily Quote Push
- **Endpoint**: `POST /api/internal/daily-quote-push`
- **Schedule**: Every 5-10 minutes (e.g., `*/5 * * * *`)
- **Header**: `X-Cron-Secret: <your-CRON_SECRET>`

Example cURL:
```bash
curl -X POST https://api.yourapp.com/api/internal/daily-quote-push \
  -H "X-Cron-Secret: your-cron-secret-here"
```

---

## Environment Variable Checklist

Before deploying, verify these are set:

- [ ] `ENVIRONMENT` - Set to "production"
- [ ] `MONGODB_URI` - Valid MongoDB connection string
- [ ] `DATABASE_NAME` - Production database name
- [ ] `SECRET_KEY` - Generated unique secret (64 hex chars)
- [ ] `CRON_SECRET` - Generated unique secret (64 hex chars)
- [ ] `FIREBASE_CREDENTIALS_PATH` - Path to Firebase credentials
- [ ] Cron jobs configured for quote init and push

---

## Testing Environment

For running tests, create a `.env.test` file or set these in your CI/CD:

```bash
ENVIRONMENT=test
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=smriti_test
SECRET_KEY=test-secret-key-for-testing-only-not-production
CRON_SECRET=test-cron-secret-for-testing-only
```
