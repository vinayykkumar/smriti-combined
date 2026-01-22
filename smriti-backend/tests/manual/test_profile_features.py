import requests
import time
import sys

# IMPORTANT: Before running tests, update your .env file:
# Comment out: DATABASE_NAME=smriti
# Uncomment: DATABASE_NAME=smriti-test
# This ensures test data doesn't mix with production data.

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"
POSTS_URL = f"{BASE_URL}/posts"
USERS_URL = f"{BASE_URL}/users"

# Test Credentials
USERNAME = "profile_test_user"
PASSWORD = "password123"
EMAIL = "profile_test@example.com"

def test_profile_features():
    print("=" * 50)
    print("TESTING PROFILE FEATURES")
    print("=" * 50)

    # 0. Signup/Login
    print("\n[Step 0] Auth: Signup or Login")

    # 0.1 Check Username Availability
    print("Checking username availability...")
    resp = requests.get(f"{AUTH_URL}/check-username/{USERNAME}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Check username '{USERNAME}': {data.get('message')} (Available: {data.get('available')})")
    else:
        print(f"[FAIL] Check username failed: {resp.text}")

    # Try signup
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "email": EMAIL,
        "display_name": "Profile Tester"
    }
    
    token = None
    
    try:
        resp = requests.post(f"{AUTH_URL}/signup", json=payload)
        
        if resp.status_code == 201:
            print("[OK] Signup successful")
            token = resp.json()["data"]["token"]
        elif resp.status_code == 409:
            print("[INFO] User exists, logging in...")
            resp = requests.post(f"{AUTH_URL}/login", json={"username": USERNAME, "password": PASSWORD})
            if resp.status_code == 200:
                 print("[OK] Login successful")
                 token = resp.json()["data"]["token"]
            else:
                print(f"[FAIL] Login failed: {resp.text}")
                return
        else:
            print(f"[FAIL] Signup failed: {resp.text}")
            return
    except Exception as e:
         print(f"[FAIL] Connection error: {e}")
         print("Make sure the server is running on localhost:8000")
         return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a post
    print("\n[Step 1] Create a post")
    post_files = {
        'content_type': (None, 'note'),
        'title': (None, 'My Profile Test Post'),
        'text_content': (None, 'Testing profile stats and feed.')
    }
    resp = requests.post(f"{POSTS_URL}/", files=post_files, headers=headers)
    if resp.status_code == 201:
        print("[OK] Post created")
        post_id = resp.json()["post"]["postId"]
    else:
        print(f"[FAIL] Create post failed: {resp.text}")
        return

    # 2. Get User Profile (Check Stats)
    print("\n[Step 2] Get User Profile (GET /users/me)")
    resp = requests.get(f"{USERS_URL}/me", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Response data keys: {data.keys()}")
        
        if "data" in data and "user" in data["data"]:
            user_data = data["data"]["user"]
            print(f"User: {user_data.get('username')}")
            print(f"Post Count: {user_data.get('post_count')}")
            
            if user_data.get('post_count') is not None and user_data.get('post_count') >= 1:
                 print("[OK] Post count verified (>= 1)")
            else:
                 print("[FAIL] Post count verification failed (None or 0)")
            
            if "joined_at" in user_data:
                 print(f"[OK] joined_at field present: {user_data['joined_at']}")
            else:
                 print("[FAIL] joined_at field missing")
        else:
            print(f"[FAIL] Unexpected response structure: {data}")
    else:
        print(f"[FAIL] Get profile failed: {resp.text}")

    # 3. Get My Posts (Feed)
    print("\n[Step 3] Get My Posts (GET /posts/me)")
    resp = requests.get(f"{POSTS_URL}/me", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        # Expecting structure: {success, status, results, data: {posts: []}}
        if "data" in data and "posts" in data["data"]:
            posts = data["data"]["posts"]
            print(f"Found {len(posts)} posts")
            
            # Verify the created post is in the list
            found = any(p["postId"] == post_id for p in posts)
            if found:
                print(f"[OK] Created post {post_id} found in feed")
            else:
                print(f"[FAIL] Created post {post_id} NOT found in feed")
        else:
             print(f"[FAIL] Unexpected response structure: {data}")
    else:
        print(f"[FAIL] Get my posts failed: {resp.text}")

    # 4. Delete Post
    print(f"\n[Step 4] Delete Post {post_id}")
    resp = requests.delete(f"{POSTS_URL}/{post_id}", headers=headers)
    if resp.status_code == 200:
        print("[OK] Post deleted successfully")
    elif resp.status_code == 404:
        print("[FAIL] Post not found (already deleted?)")
    else:
        print(f"[FAIL] Delete post failed: {resp.text}")

    # 5. Verify Post Count decreased
    print("\n[Step 5] Verify Post Count Decreased")
    resp = requests.get(f"{USERS_URL}/me", headers=headers)
    if resp.status_code == 200:
        user_data = resp.json()["data"]["user"]
        print(f"New Post Count: {user_data.get('post_count')}")
    else:
        print(f"[FAIL] Get profile failed: {resp.text}")

if __name__ == "__main__":
    test_profile_features()
