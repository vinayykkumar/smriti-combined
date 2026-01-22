# Backend API Specification for Push Notifications

## Overview
This document outlines the backend changes needed to send push notifications to all users when someone creates a post.

---

## 1. Database Schema Changes

### Add Push Token Storage

**New Table: `push_tokens`**
```sql
CREATE TABLE push_tokens (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    device_type VARCHAR(20),  -- 'android' or 'ios'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);
```

**Or add to existing users table:**
```sql
ALTER TABLE users 
ADD COLUMN push_token VARCHAR(255),
ADD COLUMN push_token_updated_at TIMESTAMP;
```

---

## 2. Required API Endpoints

### Endpoint 1: Register/Update Push Token

**Purpose:** Save user's push token when they login

```
POST /api/users/push-token
```

**Headers:**
```
Authorization: Bearer {user_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "push_token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
  "device_type": "android"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Push token registered successfully"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid token format"
}
```

**Backend Implementation (Python/FastAPI):**
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class PushTokenRequest(BaseModel):
    push_token: str
    device_type: str

@router.post("/users/push-token")
async def register_push_token(
    request: PushTokenRequest,
    current_user = Depends(get_current_user)
):
    try:
        # Save or update push token in database
        db_push_token = PushToken(
            user_id=current_user.id,
            token=request.push_token,
            device_type=request.device_type
        )
        db.add(db_push_token)
        db.commit()
        
        return {"success": True, "message": "Push token registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Endpoint 2: Send Notification to All Users (Internal)

**Purpose:** Send push notification when post is created

This is **internal** - called by your create post endpoint

**Function Implementation:**
```python
import requests
from typing import List

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

async def send_push_notification_to_all_users(
    title: str,
    body: str,
    data: dict = None,
    exclude_user_id: str = None
):
    """
    Send push notification to all users except the one who created the post
    
    Args:
        title: Notification title
        body: Notification message
        data: Additional data to send
        exclude_user_id: User ID to exclude (post creator)
    """
    
    # Get all active push tokens (exclude post creator)
    query = db.query(PushToken)
    if exclude_user_id:
        query = query.filter(PushToken.user_id != exclude_user_id)
    
    push_tokens = query.all()
    
    if not push_tokens:
        return {"success": True, "sent": 0}
    
    # Prepare messages for Expo Push API
    messages = []
    for token in push_tokens:
        messages.append({
            "to": token.token,
            "sound": "default",
            "title": title,
            "body": body,
            "data": data or {},
            "priority": "high",
            "channelId": "default"
        })
    
    # Send to Expo Push Notification service
    # Expo allows batching up to 100 notifications per request
    batch_size = 100
    total_sent = 0
    
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        
        try:
            response = requests.post(
                EXPO_PUSH_URL,
                json=batch,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                total_sent += len(batch)
                
                # Check for invalid tokens and remove them
                results = response.json()
                for idx, result in enumerate(results.get('data', [])):
                    if result.get('status') == 'error':
                        error_type = result.get('details', {}).get('error')
                        if error_type in ['DeviceNotRegistered', 'InvalidCredentials']:
                            # Remove invalid token from database
                            invalid_token = batch[idx]['to']
                            db.query(PushToken).filter(
                                PushToken.token == invalid_token
                            ).delete()
                            db.commit()
            else:
                print(f"Failed to send batch: {response.text}")
                
        except Exception as e:
            print(f"Error sending push notifications: {e}")
            continue
    
    return {"success": True, "sent": total_sent}
```

---

### Endpoint 3: Update Create Post to Send Notifications

**Modify existing:** `POST /api/posts/`

**Add notification trigger after post creation:**

```python
@router.post("/posts/")
async def create_post(
    post_data: PostCreate,
    current_user = Depends(get_current_user)
):
    try:
        # Create post (existing code)
        new_post = Post(
            user_id=current_user.id,
            title=post_data.title,
            text_content=post_data.text_content,
            content_type=post_data.content_type
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        # ✨ NEW: Send push notification to all other users
        await send_push_notification_to_all_users(
            title=f"New Reflection from {current_user.username}",
            body=f"{post_data.title}",
            data={
                "post_id": str(new_post.id),
                "screen": "post_detail"
            },
            exclude_user_id=current_user.id  # Don't notify post creator
        )
        
        return {
            "success": True,
            "post": new_post.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 3. Environment Variables

Add to your `.env` file:

```bash
# Push Notifications
EXPO_PUSH_URL=https://exp.host/--/api/v2/push/send
ENABLE_PUSH_NOTIFICATIONS=true
```

---

## 4. Installation Requirements

**Python packages needed:**
```bash
pip install requests
```

Add to `requirements.txt`:
```
requests>=2.28.0
```

---

## 5. Testing the Backend

### Test 1: Register Push Token
```bash
curl -X POST https://smriti-backend-r293.onrender.com/api/users/push-token \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "push_token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
    "device_type": "android"
  }'
```

### Test 2: Create Post (Should Trigger Notifications)
```bash
curl -X POST https://smriti-backend-r293.onrender.com/api/posts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "content_type=note&title=Test&text_content=Description"
```

### Test 3: Manually Send Test Notification
```python
# Test script: test_push.py
import requests

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

def send_test_notification(token):
    message = {
        "to": token,
        "sound": "default",
        "title": "Test Notification",
        "body": "This is a test from Smriti backend",
        "priority": "high"
    }
    
    response = requests.post(
        EXPO_PUSH_URL,
        json=[message],
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )
    
    print(response.json())

# Usage:
send_test_notification("ExponentPushToken[your-test-token]")
```

---

## 6. Error Handling

### Handle Invalid Tokens
```python
def handle_push_response(response_data, sent_tokens):
    """Remove invalid tokens from database"""
    for idx, result in enumerate(response_data.get('data', [])):
        if result.get('status') == 'error':
            error_details = result.get('details', {})
            error_type = error_details.get('error')
            
            # Remove invalid tokens
            if error_type in ['DeviceNotRegistered', 'InvalidCredentials']:
                invalid_token = sent_tokens[idx]
                db.query(PushToken).filter(
                    PushToken.token == invalid_token
                ).delete()
                db.commit()
                print(f"Removed invalid token: {invalid_token}")
```

---

## 7. Implementation Checklist

**Backend Developer Tasks:**
- [ ] Add `push_tokens` table to database
- [ ] Create `POST /api/users/push-token` endpoint
- [ ] Implement `send_push_notification_to_all_users()` function
- [ ] Update `POST /api/posts/` to call notification function
- [ ] Add error handling for invalid tokens
- [ ] Test with Expo Push tool
- [ ] Deploy to production

---

## 8. Frontend Changes (Will Implement After Backend Ready)

Once backend is ready, frontend will:
1. Get push token on login
2. Send token to backend via `/api/users/push-token`
3. Update token on app restart
4. Handle incoming notifications

---

## Summary

**What Backend Needs to Do:**
1. Store push tokens when users login
2. Fetch all push tokens (except post creator)
3. Send notification via Expo Push API when post created
4. Clean up invalid tokens

**API Calls Flow:**
```
User A logs in → Send token to backend → Store in DB
User A creates post → Backend gets all tokens → Send to Expo API → All users notified
```

**Expo Push API is free** and handles all the heavy lifting!
