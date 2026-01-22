import requests

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("INSTAGRAM MODEL - AUTHENTICATION TESTING")
print("=" * 80)

# Test 1: Signup with username + email
print("\n### TEST 1: Signup with Username + Email")
response = requests.post(f"{BASE_URL}/api/auth/signup", json={
    "username": "johndoe",
    "password": "test123",
    "email": "john@example.com"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 2: Signup with username + phone
print("\n### TEST 2: Signup with Username + Phone")
response = requests.post(f"{BASE_URL}/api/auth/signup", json={
    "username": "janedoe",
    "password": "test123",
    "phone": "+1234567890"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 3: Signup with username + email + display_name
print("\n### TEST 3: Signup with Username + Email + Display Name")
response = requests.post(f"{BASE_URL}/api/auth/signup", json={
    "username": "bobsmith",
    "password": "test123",
    "email": "bob@example.com",
    "display_name": "Bob Smith"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 4: Signup without email or phone (should fail)
print("\n### TEST 4: Signup without Email or Phone (Should Fail)")
response = requests.post(f"{BASE_URL}/api/auth/signup", json={
    "username": "failuser",
    "password": "test123"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 5: Login with username
print("\n### TEST 5: Login with Username")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "johndoe",
    "password": "test123"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 6: Login with email
print("\n### TEST 6: Login with Email")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "john@example.com",
    "password": "test123"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 7: Login with phone
print("\n### TEST 7: Login with Phone")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "+1234567890",
    "password": "test123"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 8: Duplicate username
print("\n### TEST 8: Duplicate Username (Should Fail)")
response = requests.post(f"{BASE_URL}/api/auth/signup", json={
    "username": "johndoe",
    "password": "test123",
    "email": "different@example.com"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "=" * 80)
print("TESTING COMPLETE")
print("=" * 80)
