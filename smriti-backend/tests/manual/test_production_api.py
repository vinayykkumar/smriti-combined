import requests
import json

PROD_URL = "https://smriti-backend-r293.onrender.com"

print("=" * 80)
print("TESTING PRODUCTION API ON RENDER")
print("=" * 80)

# Test 1: Health check
print("\n### Test 1: Health Check")
try:
    response = requests.get(f"{PROD_URL}/health", timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Login
print("\n### Test 2: Login with Production Account")
try:
    response = requests.post(
        f"{PROD_URL}/api/auth/login",
        json={"username": "win_i", "password": "test@12345"},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        token = data['data']['token']
        
        # Test 3: Get Posts
        print("\n### Test 3: GET /api/posts/ (with trailing slash)")
        response = requests.get(
            f"{PROD_URL}/api/posts/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 4: Get Posts without trailing slash
        print("\n### Test 4: GET /api/posts (without trailing slash)")
        response = requests.get(
            f"{PROD_URL}/api/posts",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 404:
            print(f"Response: 404 Not Found (as expected without trailing slash)")
        else:
            print(f"Response: {response.text[:200]}")
        
        print("\n" + "=" * 80)
        print("✅ PRODUCTION API TEST COMPLETE")
        print("=" * 80)
        
except Exception as e:
    print(f"❌ Error: {e}")
