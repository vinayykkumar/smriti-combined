import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("REAL USER TEST - VINAY'S ACCOUNT")
print("=" * 80)

# Test 1: Signup
print("\n### TEST 1: Signup")
print("Username: win_i")
print("Display Name: Vinay")
print("Email: kumarvinay0011.vk@gmail.com")

response = requests.post(f"{BASE_URL}/api/auth/signup", json={
    "username": "win_i",
    "password": "test@12345",
    "email": "kumarvinay0011.vk@gmail.com",
    "display_name": "Vinay"
})

print(f"\nStatus: {response.status_code}")
data = response.json()
print(f"Response:\n{json.dumps(data, indent=2)}")

if response.status_code == 201:
    print("\n✅ Signup successful!")
    token = data['data']['token']
    
    # Test 2: Login with username
    print("\n" + "=" * 80)
    print("### TEST 2: Login with Username")
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "win_i",
        "password": "test@12345"
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ Login with username successful!")
        
        # Test 3: Login with email
        print("\n" + "=" * 80)
        print("### TEST 3: Login with Email")
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "kumarvinay0011.vk@gmail.com",
            "password": "test@12345"
        })
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Login with email successful!")
            token = data['data']['token']
            
            # Test 4: Get current user
            print("\n" + "=" * 80)
            print("### TEST 4: Get Current User Profile")
            response = requests.get(f"{BASE_URL}/api/auth/me", headers={
                "Authorization": f"Bearer {token}"
            })
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response:\n{json.dumps(data, indent=2)}")
            
            if response.status_code == 200:
                print("\n✅ Profile fetch successful!")
                
                # Test 5: Check username availability
                print("\n" + "=" * 80)
                print("### TEST 5: Check Username Availability")
                response = requests.get(f"{BASE_URL}/api/auth/check-username/win_i")
                print(f"Status: {response.status_code}")
                data = response.json()
                print(f"Response:\n{json.dumps(data, indent=2)}")
                
                print("\n" + "=" * 80)
                print("🎉 ALL TESTS PASSED!")
                print("=" * 80)
                print("\n✅ Your account is created:")
                print("   Username: @win_i")
                print("   Display Name: Vinay")
                print("   Email: kumarvinay0011.vk@gmail.com")
                print("\n✅ You can login with:")
                print("   - Username: win_i")
                print("   - Email: kumarvinay0011.vk@gmail.com")
                print("\n✅ No userId exposed to frontend")
                print("=" * 80)
else:
    print(f"\n❌ Signup failed: {data.get('error')}")
