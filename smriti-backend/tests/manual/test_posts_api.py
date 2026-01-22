import requests

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("TESTING POSTS API")
print("=" * 80)

# First, login to get a token
print("\n### Step 1: Login to get token")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "win_i",
    "password": "test@12345"
})

if response.status_code == 200:
    token = response.json()['data']['token']
    print(f"✅ Login successful, got token")
    
    # Test GET /api/posts/
    print("\n### Step 2: GET /api/posts/ (with trailing slash)")
    response = requests.get(f"{BASE_URL}/api/posts/", headers={
        "Authorization": f"Bearer {token}"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test GET /api/posts (without trailing slash)
    print("\n### Step 3: GET /api/posts (without trailing slash)")
    response = requests.get(f"{BASE_URL}/api/posts", headers={
        "Authorization": f"Bearer {token}"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    # Test POST /api/posts/ (create a note)
    print("\n### Step 4: POST /api/posts/ (create note)")
    from io import BytesIO
    
    files = {
        'content_type': (None, 'note'),
        'title': (None, 'Test Post'),
        'text_content': (None, 'This is a test post from API testing')
    }
    
    response = requests.post(
        f"{BASE_URL}/api/posts/",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
else:
    print(f"❌ Login failed: {response.json()}")
