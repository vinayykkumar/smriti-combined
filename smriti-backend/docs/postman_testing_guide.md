# Postman Testing Guide

## Step 1: Import the Collection

1. Open Postman
2. Click **Import** button (top left)
3. Click **Upload Files**
4. Select `Smriti_API.postman_collection.json` from your project root
5. Click **Import**

You should now see "Smriti Backend API" in your collections.

---

## Step 2: Verify Collection Variables

1. Click on the collection name "Smriti Backend API"
2. Go to the **Variables** tab
3. You should see:
   - `base_url`: `https://smriti-backend-r293.onrender.com`
   - `token`: (empty - will be auto-filled after login)

---

## Step 3: Test in Order

### A. Health Checks (No Auth Required)

**1. Health Check**
- Folder: Health
- Request: Health Check
- Click **Send**
- Expected: 200 OK
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Smriti API"
}
```

**2. Database Health**
- Request: Database Health
- Click **Send**
- Expected: 200 OK

---

### B. Authentication

**3. Check Username Availability**
- Folder: Authentication
- Request: Check Username Availability
- Edit the URL to check any username (e.g., `/check-username/johndoe`)
- Click **Send**
- Expected: 200 OK with `available: true` or `false`

**4. Login with Username** ⭐ (Do this first!)
- Request: Login with Username
- Body is pre-filled with:
```json
{
  "username": "win_i",
  "password": "test@12345"
}
```
- Click **Send**
- Expected: 200 OK
- **Important:** The token will be automatically saved to the collection variable!
- Check the **Console** (bottom) - you should see "Token saved: eyJhbGci..."

**5. Login with Email** (Alternative)
- Request: Login with Email
- Body is pre-filled with email
- Click **Send**
- Token will be auto-saved

**6. Get Current User**
- Request: Get Current User
- Click **Send**
- Expected: 200 OK with your user profile
- Note: Uses the token automatically from collection variable

**7. Signup** (Optional - creates new user)
- Request: Signup
- Edit the body to use a unique username and email
- Click **Send**
- Expected: 201 Created

---

### C. Posts (Requires Authentication)

**Make sure you've logged in first!** The token should be in collection variables.

**8. Get All Posts**
- Folder: Posts
- Request: Get All Posts
- Click **Send**
- Expected: 200 OK
```json
{
  "success": true,
  "data": {
    "count": 1,
    "posts": [...]
  }
}
```

**9. Create Note Post**
- Request: Create Note Post
- Body (form-data) is pre-filled:
  - `content_type`: note
  - `title`: My First Note
  - `text_content`: This is a test note
- Click **Send**
- Expected: 201 Created
- Copy the `postId` from response for deletion test

**10. Create Link Post**
- Request: Create Link Post
- Body is pre-filled
- Click **Send**
- Expected: 201 Created

**11. Create Document Post**
- Request: Create Document Post
- In the `document` field, click **Select Files** and choose a PDF/DOC file
- Click **Send**
- Expected: 201 Created

**12. Delete Post**
- Request: Delete Post
- Replace `POST_ID_HERE` in the URL with an actual post ID (from step 9)
- Click **Send**
- Expected: 200 OK

---

## Important Notes

### Trailing Slash
Notice all POST/GET requests to `/api/posts/` have a trailing slash. This is required!

### Auto Token Management
The collection has scripts that automatically save the token after login. You don't need to copy-paste it manually.

### Testing Flow
1. Login (saves token)
2. All other authenticated requests use the saved token automatically
3. If you get 401 errors, login again

### Collection Variables
- `base_url`: Change this to `http://localhost:8000` to test locally
- `token`: Auto-managed, don't edit manually

---

## Troubleshooting

### 401 Unauthorized
- Make sure you've logged in first
- Check the collection variable `token` has a value
- Try logging in again

### 404 Not Found on Posts
- Make sure the URL has a trailing slash: `/api/posts/`
- Not: `/api/posts`

### 400 Bad Request
- Check the request body has all required fields
- For posts, make sure `content_type` is one of: `note`, `link`, `document`

---

## Quick Test Sequence

For a complete test run:

1. **Health Check** → Verify API is up
2. **Login with Username** → Get token (auto-saved)
3. **Get Current User** → Verify token works
4. **Get All Posts** → See existing posts
5. **Create Note Post** → Create a post
6. **Get All Posts** → Verify post was created
7. **Delete Post** → Clean up

---

## Testing Production vs Local

**Production (Default):**
- `base_url`: `https://smriti-backend-r293.onrender.com`

**Local:**
1. Click on collection
2. Go to Variables tab
3. Change `base_url` to `http://localhost:8000`
4. Save
5. Make sure your local server is running

---

## Expected Results Summary

| Request | Status | Auto-saves Token? |
|---------|--------|-------------------|
| Health Check | 200 | No |
| Check Username | 200 | No |
| Signup | 201 | Yes |
| Login | 200 | Yes |
| Get Current User | 200 | No |
| Get Posts | 200 | No |
| Create Post | 201 | No |
| Delete Post | 200 | No |

---

## Success!

If all requests return the expected status codes, your API is working perfectly! 🎉

You can now share this collection with your frontend team for reference.
