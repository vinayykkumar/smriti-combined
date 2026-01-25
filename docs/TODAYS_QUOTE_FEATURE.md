# Today's Quote Feature

## Overview

The Today's Quote feature delivers one quote per day to each user via push notification. The quote is randomly selected from existing posts in the database. Users receive their quote at a random time during their "day" - which is defined by sunrise-to-sunrise at their location.

**Key design decisions:**
- We don't track which quotes a user has seen. Each day's quote is independent.
- The "day" is based on sunrise, not midnight. This feels more natural.
- Quotes are saved to the database even if push notifications fail, so users can always see their quote in the app.

---

## Architecture

### Backend Components

```
app/quotes/
├── __init__.py
├── constants.py       # Configuration constants
├── dependencies.py    # FastAPI dependencies (cron auth)
├── extraction.py      # Quote text extraction from posts
├── repository.py      # Database operations for user_daily_quotes
├── router.py          # API endpoints
├── schemas.py         # Pydantic models for requests/responses
├── service.py         # Business logic
└── sunrise.py         # Sunrise calculations using astral library
```

### Frontend Components

```
src/
├── contexts/QuoteContext.js     # State management for quotes
├── hooks/useQuote.js            # Context accessor hook
├── components/
│   ├── quotes/TodayQuoteCard.js # Home screen card widget
│   └── common/QuotePopup.js     # Modal for full quote display
├── screens/PastQuotesScreen.js  # Quote history screen
└── services/api/quotes.js       # API client functions
```

---

## Sunrise and Day Key

### Why Sunrise?

Traditional midnight-based days feel arbitrary. Using sunrise as the day boundary means:
- The "day" starts when users typically wake up
- Night owls at 2 AM are still in "yesterday"
- It feels more aligned with human rhythms

### How It Works

The `sunrise.py` module uses the [astral](https://pypi.org/project/astral/) library:

```python
get_sunrise_info_for_user(
    user_timezone: Optional[str],
    user_latitude: Optional[float],
    user_longitude: Optional[float],
    reference_time: Optional[datetime] = None
) -> dict
```

Returns:
- `day_key`: The current day identifier (YYYY-MM-DD format)
- `day_sunrise_utc`: When this day started (sunrise) in UTC
- `next_sunrise_utc`: When this day ends (next sunrise) in UTC
- `timezone`: The timezone used for calculation

### Handling Missing Location

If a user hasn't provided location/timezone:
1. Uses `TIMEZONE_COORDINATES` mapping for common timezones
2. Falls back to UTC if timezone is unknown
3. Uses representative city coordinates for the timezone

### Polar Regions

In polar regions where sunrise may not occur:
- Falls back to 6 AM local time as "sunrise"
- Still provides a sensible day boundary

---

## Timezone and user_daily_quotes Collection

### User Timezone Storage

Users can update their timezone via:
```
PATCH /api/users/me
{
    "timezone": "America/New_York",  // IANA timezone string
    "latitude": 40.7128,             // Optional
    "longitude": -74.0060            // Optional
}
```

Timezone is validated against IANA timezone database using `ZoneInfo`.

### user_daily_quotes Collection

One document per user per day:

```javascript
{
    "_id": ObjectId,
    "user_id": "507f1f77bcf86cd799439011",
    "day_key": "2026-01-25",

    // Timing
    "day_sunrise_utc": ISODate("2026-01-25T12:00:00Z"),
    "next_sunrise_utc": ISODate("2026-01-26T12:01:00Z"),
    "scheduled_push_time_utc": ISODate("2026-01-25T15:30:00Z"),

    // Status
    "push_sent": true,
    "push_sent_at_utc": ISODate("2026-01-25T15:30:05Z"),

    // Quote data (set when push is sent)
    "quote_text": "The best time to plant a tree...",
    "source_post_id": "507f1f77bcf86cd799439012",
    "source_author_user_id": "507f1f77bcf86cd799439013",
    "source_author_username": "wise_user",

    // Metadata
    "created_at_utc": ISODate("2026-01-25T06:00:00Z"),
    "updated_at_utc": ISODate("2026-01-25T15:30:05Z")
}
```

**Indexes:**
- `(user_id, day_key)` - unique, for lookups
- `(push_sent, scheduled_push_time_utc)` - for cron job queries
- `(user_id, push_sent, day_key)` - for history queries

---

## Quote Extraction

### How Quotes Are Selected

The `pick_random_quote()` function in `extraction.py`:

1. Queries all posts with `title` or `text_content`
2. Random samples 10 posts
3. For each post, tries to extract a usable quote
4. Returns first successful extraction or `None`

### Text Extraction Rules

`extract_quote_from_text(text, max_length=200)`:

1. Normalizes whitespace
2. If entire text fits (≤ 200 chars) and is ≥ 10 chars, use it
3. Otherwise, try to fit complete sentences
4. If first sentence is too long, truncate at word boundary
5. Returns `None` if text is unusable (< 10 chars after processing)

### Quote Data Structure

```python
{
    "quote_text": "The extracted quote text (max 200 chars)",
    "post_id": "507f1f77bcf86cd799439012",
    "author_user_id": "507f1f77bcf86cd799439013",  # Optional
    "author_username": "wise_user"  # Optional
}
```

---

## Cron Endpoints and CRON_SECRET

### Authentication

Internal cron endpoints require the `X-Cron-Secret` header:

```bash
curl -X POST https://api.example.com/api/internal/daily-quote-init \
  -H "X-Cron-Secret: your-secret-here"
```

Set `CRON_SECRET` in environment variables. If not configured, endpoints return 500.

### POST /api/internal/daily-quote-init

**Run hourly.** Initializes daily quote records for all users.

For each user:
1. Determine their current day (based on sunrise)
2. Check if record exists for this day
3. If not, create record with random scheduled push time

Response:
```json
{
    "initialized_count": 150,
    "skipped_count": 50,
    "error_count": 0
}
```

### POST /api/internal/daily-quote-push

**Run every 5-10 minutes.** Sends pending push notifications.

For each pending record whose time has passed:
1. Pick a random quote from posts
2. Save quote to database (even if no posts available)
3. Send push notification (if user has device tokens)
4. Mark record as sent

Response:
```json
{
    "processed_count": 25,
    "sent_count": 20,
    "no_quote_count": 2,
    "no_tokens_count": 3,
    "error_count": 0
}
```

**Edge cases handled:**
- `no_quote_count`: No usable posts in database (quote_text saved as null)
- `no_tokens_count`: Quote saved but user has no registered devices

---

## API Endpoints

### GET /api/quotes/today

Returns today's quote status for the authenticated user.

**Response (delivered):**
```json
{
    "has_quote": true,
    "status": "delivered",
    "quote": {
        "text": "The best time to plant a tree was 20 years ago.",
        "author": {
            "user_id": "507f1f77bcf86cd799439013",
            "username": "wise_user"
        },
        "post_id": "507f1f77bcf86cd799439012",
        "day_key": "2026-01-25",
        "received_at": "2026-01-25T15:30:05Z"
    },
    "message": null
}
```

**Response (pending):**
```json
{
    "has_quote": false,
    "status": "pending",
    "quote": null,
    "message": "Your quote will arrive later today"
}
```

**Response (unavailable):**
```json
{
    "has_quote": false,
    "status": "unavailable",
    "quote": null,
    "message": "No quote available today"
}
```

### GET /api/quotes/history

Returns paginated history of past quotes.

**Query params:**
- `skip`: Number to skip (default: 0)
- `limit`: Max to return (default: 20, max: 50)

**Response:**
```json
{
    "quotes": [
        {
            "text": "Quote text here",
            "author": {"user_id": "...", "username": "..."},
            "post_id": "...",
            "day_key": "2026-01-24",
            "received_at": "2026-01-24T14:22:00Z"
        }
    ],
    "total": 45,
    "skip": 0,
    "limit": 20,
    "has_more": true
}
```

---

## Frontend: QuoteContext and QuotePopup

### QuoteContext

Provides state management for the quote feature:

```javascript
const QuoteContext = {
    // State
    isQuotePopupOpen: boolean,
    todayQuote: TodayQuoteResponse | null,
    isLoading: boolean,
    error: string | null,

    // Methods
    openQuotePopup(forceRefresh?: boolean): Promise<void>,
    closeQuotePopup(): void,
    refreshTodayQuote(): Promise<void>,
    clearQuoteData(): void,  // Called on logout
}
```

**Caching:** 5-minute cache to avoid excessive API calls. `forceRefresh=true` bypasses cache.

### QuotePopup

Modal component that displays the quote. Handles all states:

1. **Loading**: Shows spinner with "Loading your quote..."
2. **Error**: Shows error message with retry prompt
3. **Pending**: Shows clock icon with "Your quote will arrive later today"
4. **Unavailable**: Shows "No quote available today"
5. **Delivered**: Shows quote text, author (tappable), "View Full Post" button

### TodayQuoteCard

Home screen widget showing quote preview:

- **Delivered**: Shows truncated quote with "Tap to read"
- **Pending**: Shows "Your quote will arrive today"
- **Unavailable**: Hidden (returns null)

---

## today_quote Notification Handling

### Push Notification Structure

```javascript
{
    notification: {
        title: "Today's Quote",
        body: "The best time to plant a tree..."  // Truncated to 100 chars
    },
    data: {
        type: "today_quote",
        day_key: "2026-01-25",
        quote_text: "Full quote text here",
        post_id: "507f1f77bcf86cd799439012"  // Optional
    }
}
```

### Frontend Handling

In `notificationService.js`, three scenarios:

1. **Foreground** (app is open):
   - Checks `remoteMessage.data?.type === 'today_quote'`
   - Calls `openQuotePopup(true)` immediately
   - No alert shown - popup opens directly

2. **Background** (app in background):
   - Same check for quote type
   - Calls `openQuotePopup(true)` with 300ms delay
   - Delay ensures app is ready

3. **Killed** (app was closed):
   - Checks `getInitialNotification()`
   - Calls `openQuotePopup(true)` with 500ms delay
   - Longer delay for app initialization

### Provider Hierarchy

```jsx
<AuthProvider>
  <QuoteProvider>  {/* Must be above notification setup */}
    <NavigationContainer>
      <AppNavigator />
      <QuotePopup />  {/* Uses useNavigation */}
    </NavigationContainer>
  </QuoteProvider>
</AuthProvider>
```

---

## Edge Cases

### No Timezone
- Defaults to "UTC"
- Uses UTC+0 coordinates for sunrise calculation

### No Device Tokens
- Quote is still saved to database
- User can view quote in app (just won't get push)
- `no_tokens_count` tracked in cron response

### No Usable Posts
- `quote_text` saved as null
- Status returns as "unavailable"
- Frontend shows "No quote available today"

### Missing Author
- `author.user_id` and `author.username` can be null
- Frontend uses optional chaining (`author?.username`)
- "View Full Post" button hidden if no `post_id`

### Long Quotes
- Backend limits to 200 characters
- TodayQuoteCard truncates to ~80 chars for preview
- Push notification truncates to 100 chars

### Small Screens
- QuotePopup has `maxWidth: 340` and responsive padding
- Cards use percentage-based widths
- Text uses line clamping (`numberOfLines`)

---

## No Tracking

We explicitly do NOT track:
- Which quotes a user has seen before
- Quote engagement (views, taps, etc.)
- Reading time or interactions

Each day's quote is independently random. This keeps the feature simple and privacy-friendly.

---

## Test Coverage

### Unit Tests
- `tests/unit/test_sunrise.py`: 15 tests for sunrise calculations
- `tests/unit/test_extraction.py`: 23 tests for quote extraction

### Integration Tests
- `tests/integration/test_quotes_api.py`: 29 tests for:
  - Timezone validation
  - Quote response schemas
  - Cron response schemas
  - Helper functions
  - Edge cases (null author, long quotes, etc.)

Run tests:
```bash
pytest tests/unit/test_sunrise.py tests/unit/test_extraction.py tests/integration/test_quotes_api.py -v
```

---

## Deployment Checklist

1. **Environment variables:**
   - `CRON_SECRET`: Strong random secret for cron authentication

2. **Database indexes:**
   - Run repository's `ensure_indexes()` on startup

3. **Cron jobs:**
   - `/api/internal/daily-quote-init`: Run hourly
   - `/api/internal/daily-quote-push`: Run every 5-10 minutes

4. **Frontend:**
   - Ensure `QuoteProvider` wraps authenticated content
   - Register `PastQuotes` screen in navigator
