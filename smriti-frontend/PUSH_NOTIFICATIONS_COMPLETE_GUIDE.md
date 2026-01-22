# Complete Push Notifications Guide - Frontend + Backend

## Overview: How Push Notifications Work

```
┌─────────────┐          ┌─────────────┐          ┌──────────────┐          ┌─────────────┐
│   User A    │          │   Backend   │          │  Expo Push   │          │   User B    │
│   (Phone)   │          │   Server    │          │   Service    │          │   (Phone)   │
└──────┬──────┘          └──────┬──────┘          └──────┬───────┘          └──────┬──────┘
       │                        │                         │                         │
       │  1. Login              │                         │                         │
       ├───────────────────────>│                         │                         │
       │                        │                         │                         │
       │  2. Get Push Token     │                         │                         │
       │  (from Expo)           │                         │                         │
       │                        │                         │                         │
       │  3. Send Token         │                         │                         │
       │  to Backend            │                         │                         │
       ├───────────────────────>│                         │                         │
       │                        │  4. Store Token         │                         │
       │                        │  in Database            │                         │
       │                        │                         │                         │
       │  5. Create Post        │                         │                         │
       ├───────────────────────>│                         │                         │
       │                        │  6. Get All Tokens      │                         │
       │                        │  (except User A)        │                         │
       │                        │                         │                         │
       │                        │  7. Send Notification   │                         │
       │                        │  Request                │                         │
       │                        ├────────────────────────>│                         │
       │                        │                         │  8. Deliver to Devices  │
       │                        │                         ├────────────────────────>│
       │                        │                         │                         │
       │                        │                         │  9. Show Notification   │
       │                        │                         │  "New Post from A"      │
       │                        │                         │                         │
```

---

## Part 1: Frontend Implementation (React Native)

### Step 1.1: Get Push Token When User Logs In

**File:** `src/services/api.js`

Add new function to get Expo push token:

```javascript
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

/**
 * Get Expo Push Token
 * This token uniquely identifies this device for push notifications
 */
export const getExpoPushToken = async () => {
  try {
    // For Android, we need a notification channel
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
      });
    }

    // Request permissions
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      console.log('Permission not granted for push notifications');
      return null;
    }

    // Get the token
    const token = await Notifications.getExpoPushTokenAsync({
      projectId: 'bcd2f061-f216-4506-b5b8-14d909f1a7a1', // Your EAS project ID from app.json
    });
    
    return token.data; // Returns: "ExponentPushToken[xxxxxxxxxxxxxx]"
    
  } catch (error) {
    console.error('Error getting push token:', error);
    return null;
  }
};

/**
 * Register push token with backend
 */
export const registerPushToken = async (pushToken) => {
  try {
    const authToken = await getAuthToken();
    if (!authToken) return { success: false, error: 'Not authenticated' };

    const response = await fetch(`${API_BASE_URL}/users/push-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        push_token: pushToken,
        device_type: Platform.OS // 'android' or 'ios'
      })
    });

    const data = await response.json();
    return data;
    
  } catch (error) {
    console.error('Error registering push token:', error);
    return { success: false, error: error.message };
  }
};
```

### Step 1.2: Call After Login

**File:** `src/screens/LoginScreen.js` and `src/screens/AuthScreen.js`

Add this after successful login:

```javascript
import { getExpoPushToken, registerPushToken } from '../services/api';

// In your login success handler:
const handleLoginSuccess = async () => {
  // Existing login code...
  
  // Get and register push token
  const pushToken = await getExpoPushToken();
  if (pushToken) {
    await registerPushToken(pushToken);
  }
  
  // Navigate to home...
};
```

### Step 1.3: Handle Incoming Notifications

**File:** `App.js`

Add notification response listener:

```javascript
import * as Notifications from 'expo-notifications';

function AppContent() {
  // ... existing code ...

  // Listen for notification taps
  React.useEffect(() => {
    const subscription = Notifications.addNotificationResponseReceivedListener(response => {
      // User tapped the notification
      const data = response.notification.request.content.data;
      
      if (data.post_id) {
        // Navigate to post detail screen
        // setCurrentScreen('POST_DETAIL');
        // setSelectedPostId(data.post_id);
        console.log('Navigate to post:', data.post_id);
      }
    });

    return () => subscription.remove();
  }, []);
}
```

---

## Part 2: Backend Implementation (Python/FastAPI)

### Step 2.1: Database Schema

**Add push tokens table:**

```sql
CREATE TABLE push_tokens (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    device_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token (token)
);
```

### Step 2.2: API Endpoint to Register Token

**File:** `routes/users.py` (or wherever your user routes are)

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class PushTokenRequest(BaseModel):
    push_token: str
    device_type: str

@router.post("/users/push-token")
async def register_push_token(
    request: PushTokenRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Register or update user's push notification token
    """
    try:
        # Check if token already exists
        existing = db.query(PushToken).filter(
            PushToken.user_id == current_user.id
        ).first()
        
        if existing:
            # Update existing token
            existing.token = request.push_token
            existing.device_type = request.device_type
            existing.updated_at = datetime.utcnow()
        else:
            # Create new token
            new_token = PushToken(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                token=request.push_token,
                device_type=request.device_type
            )
            db.add(new_token)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Push token registered successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 2.3: Function to Send Push Notifications

**File:** `services/push_notifications.py` (new file)

```python
import requests
from typing import List, Optional
from database import get_db
from models import PushToken

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

async def send_push_notification_to_all_users(
    title: str,
    body: str,
    data: dict = None,
    exclude_user_id: str = None,
    db = None
):
    """
    Send push notification to all users (except excluded user)
    
    Args:
        title: Notification title
        body: Notification body text
        data: Additional data payload
        exclude_user_id: User ID to exclude (usually post creator)
        db: Database session
    
    Returns:
        Dict with success status and count of sent notifications
    """
    if db is None:
        db = next(get_db())
    
    # Get all push tokens (exclude specific user if needed)
    query = db.query(PushToken)
    if exclude_user_id:
        query = query.filter(PushToken.user_id != exclude_user_id)
    
    tokens = query.all()
    
    if not tokens:
        return {"success": True, "sent": 0, "message": "No tokens to send to"}
    
    # Prepare notification messages
    messages = []
    token_map = {}  # Map index to token for cleanup
    
    for idx, token_obj in enumerate(tokens):
        messages.append({
            "to": token_obj.token,
            "sound": "default",
            "title": title,
            "body": body,
            "data": data or {},
            "priority": "high",
            "channelId": "default"
        })
        token_map[idx] = token_obj.token
    
    # Send to Expo Push API (batch up to 100 per request)
    batch_size = 100
    total_sent = 0
    invalid_tokens = []
    
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        
        try:
            response = requests.post(
                EXPO_PUSH_URL,
                json=batch,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                
                # Check for errors and invalid tokens
                for idx, result in enumerate(results.get('data', [])):
                    batch_idx = i + idx
                    
                    if result.get('status') == 'ok':
                        total_sent += 1
                    elif result.get('status') == 'error':
                        error_type = result.get('details', {}).get('error')
                        
                        # Mark invalid tokens for removal
                        if error_type in ['DeviceNotRegistered', 'InvalidCredentials']:
                            invalid_tokens.append(token_map[batch_idx])
                            print(f"Invalid token found: {error_type}")
                        else:
                            print(f"Notification error: {result}")
            else:
                print(f"Expo API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error sending batch {i}-{i+batch_size}: {e}")
            continue
    
    # Clean up invalid tokens
    if invalid_tokens:
        db.query(PushToken).filter(
            PushToken.token.in_(invalid_tokens)
        ).delete(synchronize_session=False)
        db.commit()
        print(f"Removed {len(invalid_tokens)} invalid tokens")
    
    return {
        "success": True,
        "sent": total_sent,
        "invalid_removed": len(invalid_tokens)
    }
```

### Step 2.4: Update Create Post Endpoint

**File:** `routes/posts.py`

```python
from services.push_notifications import send_push_notification_to_all_users

@router.post("/posts/")
async def create_post(
    post_data: PostCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new post and notify all users"""
    try:
        # Create post (existing code)
        new_post = Post(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            title=post_data.title,
            text_content=post_data.text_content,
            content_type=post_data.content_type,
            created_at=datetime.utcnow()
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        # ✨ Send push notifications to all other users
        try:
            notification_result = await send_push_notification_to_all_users(
                title=f"New Reflection from {current_user.username}",
                body=f"{post_data.title[:100]}",  # Limit to 100 chars
                data={
                    "post_id": new_post.id,
                    "author": current_user.username,
                    "screen": "post_detail"
                },
                exclude_user_id=current_user.id,
                db=db
            )
            print(f"Notifications sent: {notification_result}")
        except Exception as e:
            # Don't fail post creation if notifications fail
            print(f"Failed to send notifications: {e}")
        
        return {
            "success": True,
            "post": new_post.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Part 3: Testing

### Test 1: Test Push Token Registration

```bash
# 1. Login and get token
curl -X POST https://smriti-backend-r293.onrender.com/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"

# 2. Register push token
curl -X POST https://smriti-backend-r293.onrender.com/api/users/push-token \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "push_token": "ExponentPushToken[test-token-here]",
    "device_type": "android"
  }'
```

### Test 2: Send Test Notification (Backend)

```python
# test_push.py
import requests

def send_test_notification():
    """Send a test notification via Expo"""
    message = {
        "to": "ExponentPushToken[your-actual-token]",
        "sound": "default",
        "title": "Test from Smriti",
        "body": "This is a test notification!",
        "data": {"test": "data"},
        "priority": "high"
    }
    
    response = requests.post(
        "https://exp.host/--/api/v2/push/send",
        json=[message],
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )
    
    print(response.json())

send_test_notification()
```

### Test 3: End-to-End Test

1. **Login with User A** → Token registered
2. **Login with User B** → Token registered  
3. **User A creates post** → Backend sends notification
4. **User B receives notification** ✅

---

## Summary: What Happens Step-by-Step

### First-Time Setup (Per User):
```
1. User opens app
2. App requests notification permission
3. User grants permission
4. App gets Expo push token from Expo servers
5. App sends token to your backend
6. Backend stores token in database
```

### When Post is Created:
```
1. User A creates post
2. Frontend calls POST /api/posts/
3. Backend saves post to database
4. Backend queries all push tokens (except User A)
5. Backend sends notification request to Expo API
6. Expo delivers to all devices
7. Users B, C, D... see notification "New post from User A"
```

## Files You Need to Modify

**Frontend:**
- ✅ Already done: App.js (notification handler)
- 🆕 Add: `src/services/api.js` (getExpoPushToken, registerPushToken)
- 🆕 Update: LoginScreen.js (call registerPushToken after login)
- 🆕 Update: AuthScreen.js (call registerPushToken after signup)

**Backend:**
- 🆕 Database: Add `push_tokens` table
- 🆕 New endpoint: `POST /api/users/push-token`
- 🆕 New file: `services/push_notifications.py`
- 🆕 Update: `POST /api/posts/` (add notification trigger)
- 🆕 Dependency: `pip install requests`

## Cost

**Expo Push Notifications are FREE!** ✅
- No limit on number of notifications
- No setup fees
- Just need your EAS project ID
