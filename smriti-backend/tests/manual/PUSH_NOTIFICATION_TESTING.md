# Firebase Push Notifications - Dev Testing Guide

## Prerequisites
1. ✅ Firebase Admin SDK initialized (backend)
2. ✅ Firebase credentials file configured
3. 📱 Frontend app with Firebase Cloud Messaging (FCM) setup
4. 📱 Physical device or emulator with Google Play Services

## Step 1: Get FCM Device Token from Frontend

You need to get the FCM token from your React Native app. Add this code temporarily:

**File: `smriti-frontend/App.js` or create a test component**

```javascript
import messaging from '@react-native-firebase/messaging';
import { useEffect } from 'react';

// Add this inside your component
useEffect(() => {
  async function getToken() {
    const token = await messaging().getToken();
    console.log('📱 FCM Token:', token);
    alert('FCM Token: ' + token);
  }
  getToken();
}, []);
```

## Step 2: Run the Test Script

Once you have the token:

```bash
cd c:\Users\Vinay\OneDrive\Desktop\smriti-backend
poetry run python tests/manual/test_push_notification.py
```

Enter your FCM token when prompted.

## Step 3: Test via API Endpoint

### Register a device token:

```bash
# 1. Login first
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"

# 2. Register FCM token
curl -X POST http://localhost:8000/api/v1/notifications/register-token \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_FCM_TOKEN_HERE",
    "platform": "android"
  }'
```

## Step 4: Test End-to-End

1. **User A**: Login and register device token
2. **User B**: Login and register device token  
3. **User A**: Create a new post
4. **User B**: Should receive notification! 🎉

## Troubleshooting

### "Firebase not initialized"
- Check `.env` has `FIREBASE_CREDENTIALS_PATH` set
- Verify the credentials file exists at that path

### "No module named 'firebase_admin'"
- Run: `poetry install`

### Token invalid
- Make sure you're using an FCM token, not an Expo token
- Token should start with something like `dXXXXXX...` or `eXXXXXX...`

### No notification received
- Check device has internet connection
- Verify app has notification permissions
- Check Firebase Console for delivery status
