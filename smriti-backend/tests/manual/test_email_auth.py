import requests
import json

BASE_URL = "http://localhost:8000"

def test_case(name, method, endpoint, data=None, headers=None, expected_status=None):
    """Run a single test case"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers or {})
        elif method == "GET":
            response = requests.get(url, headers=headers or {})
        
        status = response.status_code
        try:
            body = response.json()
        except:
            body = response.text
        
        result = "✅ PASS" if (expected_status is None or status == expected_status) else "❌ FAIL"
        
        print(f"\n{result} | {name}")
        print(f"Status: {status}")
        print(f"Response: {json.dumps(body, indent=2)[:200]}")
        
        return {"name": name, "status": status, "body": body, "result": result}
    except Exception as e:
        print(f"\n❌ ERROR | {name}")
        print(f"Error: {str(e)}")
        return {"name": name, "error": str(e), "result": "❌ ERROR"}

print("=" * 80)
print("EMAIL AUTHENTICATION - COMPREHENSIVE EDGE CASE TESTING")
print("=" * 80)

results = []

# Test 1: Duplicate Username Detection
print("\n\n### TEST 1: Duplicate Username Detection")
results.append(test_case(
    "Create first user",
    "POST", "/api/auth/signup",
    {"username": "dupuser", "email": "dup1@test.com", "password": "test123"},
    expected_status=201
))

results.append(test_case(
    "Try duplicate username",
    "POST", "/api/auth/signup",
    {"username": "dupuser", "email": "dup2@test.com", "password": "test123"},
    expected_status=409
))

# Test 2: Duplicate Email Detection
print("\n\n### TEST 2: Duplicate Email Detection")
results.append(test_case(
    "Create user with email",
    "POST", "/api/auth/signup",
    {"username": "emailuser1", "email": "shared@test.com", "password": "test123"},
    expected_status=201
))

results.append(test_case(
    "Try duplicate email",
    "POST", "/api/auth/signup",
    {"username": "emailuser2", "email": "shared@test.com", "password": "test123"},
    expected_status=409
))

# Test 3: Login with Username
print("\n\n### TEST 3: Login with Username")
results.append(test_case(
    "Login with username",
    "POST", "/api/auth/login",
    {"username": "dupuser", "password": "test123"},
    expected_status=200
))

# Test 4: Login with Email
print("\n\n### TEST 4: Login with Email")
results.append(test_case(
    "Login with email",
    "POST", "/api/auth/login",
    {"email": "dup1@test.com", "password": "test123"},
    expected_status=200
))

# Test 5: Login with Neither
print("\n\n### TEST 5: Login without Username or Email")
results.append(test_case(
    "Login with only password",
    "POST", "/api/auth/login",
    {"password": "test123"},
    expected_status=400
))

# Test 6: Missing Email on Signup
print("\n\n### TEST 6: Missing Required Fields")
results.append(test_case(
    "Signup without email",
    "POST", "/api/auth/signup",
    {"username": "noemail", "password": "test123"},
    expected_status=400
))

results.append(test_case(
    "Signup without username",
    "POST", "/api/auth/signup",
    {"email": "nouser@test.com", "password": "test123"},
    expected_status=400
))

results.append(test_case(
    "Signup without password",
    "POST", "/api/auth/signup",
    {"username": "nopass", "email": "nopass@test.com"},
    expected_status=400
))

# Test 7: Username Length Boundaries
print("\n\n### TEST 7: Username Length Validation")
results.append(test_case(
    "Username too short (2 chars)",
    "POST", "/api/auth/signup",
    {"username": "ab", "email": "short@test.com", "password": "test123"},
    expected_status=400
))

results.append(test_case(
    "Username minimum (3 chars)",
    "POST", "/api/auth/signup",
    {"username": "abc", "email": "min@test.com", "password": "test123"},
    expected_status=201
))

results.append(test_case(
    "Username maximum (50 chars)",
    "POST", "/api/auth/signup",
    {"username": "a" * 50, "email": "max@test.com", "password": "test123"},
    expected_status=201
))

results.append(test_case(
    "Username too long (51 chars)",
    "POST", "/api/auth/signup",
    {"username": "a" * 51, "email": "toolong@test.com", "password": "test123"},
    expected_status=400
))

# Test 8: Password Length Boundaries
print("\n\n### TEST 8: Password Length Validation")
results.append(test_case(
    "Password too short (5 chars)",
    "POST", "/api/auth/signup",
    {"username": "passshort", "email": "passshort@test.com", "password": "12345"},
    expected_status=400
))

results.append(test_case(
    "Password minimum (6 chars)",
    "POST", "/api/auth/signup",
    {"username": "passmin", "email": "passmin@test.com", "password": "123456"},
    expected_status=201
))

# Test 9: SQL Injection Attempts
print("\n\n### TEST 9: SQL Injection Protection")
results.append(test_case(
    "SQL in username",
    "POST", "/api/auth/signup",
    {"username": "admin' OR '1'='1", "email": "sql1@test.com", "password": "test123"},
    expected_status=201  # Should succeed but store as literal string
))

results.append(test_case(
    "SQL in password",
    "POST", "/api/auth/signup",
    {"username": "sqlpass", "email": "sql2@test.com", "password": "pass' OR '1'='1"},
    expected_status=201  # Should succeed and hash the password
))

# Test 10: XSS Attempts
print("\n\n### TEST 10: XSS Protection")
results.append(test_case(
    "XSS in username",
    "POST", "/api/auth/signup",
    {"username": "<script>alert(1)</script>", "email": "xss@test.com", "password": "test123"},
    expected_status=201  # Should succeed but store as literal string
))

# Test 11: Wrong Password
print("\n\n### TEST 11: Authentication Failures")
results.append(test_case(
    "Wrong password",
    "POST", "/api/auth/login",
    {"username": "dupuser", "password": "wrongpass"},
    expected_status=401
))

results.append(test_case(
    "Non-existent user",
    "POST", "/api/auth/login",
    {"username": "doesnotexist", "password": "test123"},
    expected_status=401
))

# Test 12: Check Username Availability
print("\n\n### TEST 12: Username Availability Check")
results.append(test_case(
    "Check existing username",
    "GET", "/api/auth/check-username/dupuser",
    expected_status=200
))

results.append(test_case(
    "Check available username",
    "GET", "/api/auth/check-username/brandnewuser999",
    expected_status=200
))

# Summary
print("\n\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

passed = sum(1 for r in results if r.get("result") == "✅ PASS")
failed = sum(1 for r in results if r.get("result") == "❌ FAIL")
errors = sum(1 for r in results if r.get("result") == "❌ ERROR")

print(f"\nTotal Tests: {len(results)}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"❌ Errors: {errors}")

if failed > 0 or errors > 0:
    print("\n\nFailed/Error Tests:")
    for r in results:
        if r.get("result") in ["❌ FAIL", "❌ ERROR"]:
            print(f"  - {r['name']}")
