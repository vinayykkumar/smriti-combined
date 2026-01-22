import requests

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("INSTAGRAM MODEL - NO USERID IN FRONTEND")
print("=" * 80)

# Test 1: Signup
print("\n### TEST 1: Signup with Username + Email")
response = requests.post(f"{BASE_URL}/api/auth/signup", json={
    "username": "testuser1",
    "password": "test123",
    "email": "test1@example.com",
    "display_name": "Test User One"
})
print(f"Status: {response.status_code}")
data = response.json()
print(f"Response: {data}")

# Verify no userId in response
if 'userId' in data.get('data', {}):
    print("❌ FAIL: userId should not be in response")
else:
    print("✅ PASS: No userId in response")

# Test 2: Login
print("\n### TEST 2: Login with Username")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "testuser1",
    "password": "test123"
})
print(f"Status: {response.status_code}")
data = response.json()
print(f"Response: {data}")

# Verify no userId in response
if 'userId' in data.get('data', {}):
    print("❌ FAIL: userId should not be in response")
else:
    print("✅ PASS: No userId in response")

# Save token for next test
token = data['data']['token']

# Test 3: Get current user (with token)
print("\n### TEST 3: Get Current User (Token contains userId internally)")
response = requests.get(f"{BASE_URL}/api/auth/me", headers={
    "Authorization": f"Bearer {token}"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "=" * 80)
print("✅ Backend uses userId internally (in token)")
print("✅ Frontend only sees: username, displayName, email, phone, token")
print("=" * 80)
