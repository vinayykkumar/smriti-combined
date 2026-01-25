# Production Deployment Checklist

## Pre-Deployment Verification

### Backend Tests
```bash
cd smriti-backend
python -m pytest tests/unit tests/integration --ignore=tests/manual -v
```
**Expected Result:** 78 passed (warnings are OK)

### Frontend Syntax Check
```bash
cd smriti-frontend
node --check src/contexts/QuoteContext.js
node --check src/hooks/useQuote.js
node --check src/services/api/quotes.js
node --check src/components/common/QuotePopup.js
node --check src/components/quotes/TodayQuoteCard.js
node --check src/screens/PastQuotesScreen.js
node --check src/services/notificationService.js
node --check src/navigation/AppNavigator.js
node --check App.js
```
**Expected Result:** All files OK

---

## Environment Variables Setup

### 1. Backend Environment Variables

Create/update `smriti-backend/.env`:

```bash
# REQUIRED
ENVIRONMENT=production
MONGODB_URI=<your-mongodb-uri>
DATABASE_NAME=<your-database-name>
SECRET_KEY=<generate-64-char-hex>
CRON_SECRET=<generate-64-char-hex>

# Firebase (for push notifications)
FIREBASE_CREDENTIALS_PATH=<path-to-credentials.json>
```

Generate secrets:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Frontend Configuration

Update API base URL in your frontend config to point to production backend.

---

## Database Setup

### Create Indexes

The quote feature requires these indexes for performance:

```python
# Run this once on your production database
from app.quotes.repository import QuoteRepository

repo = QuoteRepository(db)
await repo.ensure_indexes()
```

Or manually create:
```javascript
// MongoDB shell
db.user_daily_quotes.createIndex({ "user_id": 1, "day_key": 1 }, { unique: true })
db.user_daily_quotes.createIndex({ "push_sent": 1, "scheduled_push_time_utc": 1 })
db.user_daily_quotes.createIndex({ "user_id": 1, "push_sent": 1, "day_key": -1 })
```

---

## Cron Jobs Setup

### Option A: Using crontab (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily Quote Init - every hour
0 * * * * curl -X POST https://your-api.com/api/internal/daily-quote-init -H "X-Cron-Secret: YOUR_CRON_SECRET" >> /var/log/quote-init.log 2>&1

# Daily Quote Push - every 5 minutes
*/5 * * * * curl -X POST https://your-api.com/api/internal/daily-quote-push -H "X-Cron-Secret: YOUR_CRON_SECRET" >> /var/log/quote-push.log 2>&1
```

### Option B: Using a cron service (Railway, Render, etc.)

Configure two jobs:
1. **daily-quote-init**: POST to `/api/internal/daily-quote-init` every hour
2. **daily-quote-push**: POST to `/api/internal/daily-quote-push` every 5 minutes

Both require header: `X-Cron-Secret: <your-CRON_SECRET>`

### Option C: Using cloud scheduler (AWS, GCP, Azure)

Create scheduled tasks/functions that call the endpoints with the cron secret header.

---

## Deployment Steps

### Backend

1. Set all environment variables
2. Deploy code
3. Run database index creation (once)
4. Configure cron jobs
5. Test endpoints:
   ```bash
   # Test today's quote endpoint
   curl https://your-api.com/api/quotes/today -H "Authorization: Bearer <token>"

   # Test cron endpoint (with valid secret)
   curl -X POST https://your-api.com/api/internal/daily-quote-init -H "X-Cron-Secret: <secret>"
   ```

### Frontend

1. Update API base URL
2. Build the app:
   ```bash
   npx expo build:android
   npx expo build:ios
   ```
3. Test on device

---

## Post-Deployment Verification

### 1. Test API Endpoints

```bash
# Get today's quote (authenticated)
curl https://your-api.com/api/quotes/today \
  -H "Authorization: Bearer <user-token>"

# Get quote history (authenticated)
curl "https://your-api.com/api/quotes/history?skip=0&limit=20" \
  -H "Authorization: Bearer <user-token>"

# Test cron init
curl -X POST https://your-api.com/api/internal/daily-quote-init \
  -H "X-Cron-Secret: <your-secret>"

# Test cron push
curl -X POST https://your-api.com/api/internal/daily-quote-push \
  -H "X-Cron-Secret: <your-secret>"
```

### 2. Test Push Notifications

1. Open app on device
2. Wait for scheduled push time or trigger manually
3. Verify notification appears
4. Tap notification - should open quote popup

### 3. Test Frontend Flows

1. **Home Screen**: TodayQuoteCard should show
2. **Tap Card**: QuotePopup should open
3. **Past Quotes**: Navigate and verify list loads
4. **View Full Post**: Should navigate to user profile

---

## Monitoring

### Logs to Watch

- Cron job responses (initialized_count, sent_count, error_count)
- Push notification failures
- Database connection errors

### Expected Cron Responses

**Daily Quote Init:**
```json
{
  "initialized_count": 100,  // New users today
  "skipped_count": 900,      // Already initialized
  "error_count": 0           // Should be 0
}
```

**Daily Quote Push:**
```json
{
  "processed_count": 50,     // Users due for push
  "sent_count": 45,          // Successfully sent
  "no_quote_count": 2,       // No posts available
  "no_tokens_count": 3,      // No device tokens
  "error_count": 0           // Should be 0
}
```

---

## Troubleshooting

### "CRON_SECRET not configured"
- Set CRON_SECRET environment variable

### "Invalid cron secret"
- Verify X-Cron-Secret header matches CRON_SECRET env var

### Quotes not appearing
- Check cron jobs are running
- Verify user has timezone set
- Check database has posts with text content

### Push notifications not received
- Verify Firebase credentials
- Check user has registered device token
- Verify notification permissions on device
