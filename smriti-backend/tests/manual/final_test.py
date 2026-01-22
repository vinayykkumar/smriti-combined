import requests
from io import BytesIO
from PIL import Image
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("FINAL COMPREHENSIVE TEST - ALL FEATURES")
print("=" * 80)

test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def test(name, condition, details=""):
    if condition:
        print(f"✅ {name}")
        test_results["passed"] += 1
        test_results["tests"].append({"name": name, "status": "PASS", "details": details})
    else:
        print(f"❌ {name}")
        test_results["failed"] += 1
        test_results["tests"].append({"name": name, "status": "FAIL", "details": details})

# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================
print("\n" + "=" * 80)
print("AUTHENTICATION TESTS")
print("=" * 80)

# Test 1: Check username availability
print("\n### Test 1: Check Username Availability")
response = requests.get(f"{BASE_URL}/api/auth/check-username/available_user")
test("Username availability check", response.status_code == 200, f"Status: {response.status_code}")

# Test 2: Login with username
print("\n### Test 2: Login with Username")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "win_i",
    "password": "test@12345"
})
test("Login with username", response.status_code == 200, f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    token = data['data']['token']
    test("Token received", 'token' in data['data'], f"Token length: {len(token)}")
    test("No userId in response", 'userId' not in data['data'], "userId properly hidden")
    test("Username in response", data['data']['username'] == 'win_i', f"Username: {data['data']['username']}")
    
    # Test 3: Get current user
    print("\n### Test 3: Get Current User")
    response = requests.get(f"{BASE_URL}/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    test("Get current user", response.status_code == 200, f"Status: {response.status_code}")
    
    # ============================================================================
    # POSTS TESTS
    # ============================================================================
    print("\n" + "=" * 80)
    print("POSTS TESTS")
    print("=" * 80)
    
    # Test 4: Get all posts
    print("\n### Test 4: Get All Posts")
    response = requests.get(f"{BASE_URL}/api/posts/", headers={
        "Authorization": f"Bearer {token}"
    })
    test("Get all posts", response.status_code == 200, f"Status: {response.status_code}")
    
    if response.status_code == 200:
        posts_data = response.json()
        test("Posts response structure", 'data' in posts_data and 'posts' in posts_data['data'], 
             f"Count: {posts_data['data']['count']}")
    
    # Test 5: Create Note Post
    print("\n### Test 5: Create Note Post")
    files = {
        'content_type': (None, 'note'),
        'title': (None, 'Final Test Note'),
        'text_content': (None, 'This is a comprehensive test note')
    }
    response = requests.post(f"{BASE_URL}/api/posts/", files=files, headers={
        "Authorization": f"Bearer {token}"
    })
    test("Create note post", response.status_code == 201, f"Status: {response.status_code}")
    
    if response.status_code == 201:
        note_data = response.json()
        note_id = note_data['post']['postId']
        test("Note has postId", 'postId' in note_data['post'], f"ID: {note_id}")
    
    # Test 6: Create Link Post
    print("\n### Test 6: Create Link Post")
    files = {
        'content_type': (None, 'link'),
        'title': (None, 'Final Test Link'),
        'link_url': (None, 'https://example.com'),
        'text_content': (None, 'Test link description')
    }
    response = requests.post(f"{BASE_URL}/api/posts/", files=files, headers={
        "Authorization": f"Bearer {token}"
    })
    test("Create link post", response.status_code == 201, f"Status: {response.status_code}")
    
    if response.status_code == 201:
        link_data = response.json()
        test("Link has URL", 'linkUrl' in link_data['post'], f"URL: {link_data['post']['linkUrl']}")
    
    # Test 7: Create Image Post
    print("\n### Test 7: Create Image Post")
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    files = {
        'content_type': (None, 'image'),
        'title': (None, 'Final Test Image'),
        'text_content': (None, 'Test image caption'),
        'image': ('test.png', img_bytes.getvalue(), 'image/png')
    }
    response = requests.post(f"{BASE_URL}/api/posts/", files=files, headers={
        "Authorization": f"Bearer {token}"
    })
    test("Create image post", response.status_code == 201, f"Status: {response.status_code}")
    
    if response.status_code == 201:
        image_data = response.json()
        test("Image has imageUrl", 'imageUrl' in image_data['post'], 
             f"URL: {image_data['post']['imageUrl'][:50]}...")
        test("Image uploaded to Cloudinary", 
             'cloudinary.com' in image_data['post'].get('imageUrl', ''),
             "Cloudinary CDN confirmed")
        image_id = image_data['post']['postId']
    
    # Test 8: Verify all post types in GET
    print("\n### Test 8: Verify All Post Types")
    response = requests.get(f"{BASE_URL}/api/posts/", headers={
        "Authorization": f"Bearer {token}"
    })
    
    if response.status_code == 200:
        all_posts = response.json()['data']['posts']
        content_types = set(p['contentType'] for p in all_posts)
        test("Note posts exist", 'note' in content_types, f"Types: {content_types}")
        test("Link posts exist", 'link' in content_types, f"Types: {content_types}")
        test("Image posts exist", 'image' in content_types, f"Types: {content_types}")
    
    # Test 9: Delete post
    print("\n### Test 9: Delete Post")
    if 'image_id' in locals():
        response = requests.delete(f"{BASE_URL}/api/posts/{image_id}", headers={
            "Authorization": f"Bearer {token}"
        })
        test("Delete post", response.status_code == 200, f"Status: {response.status_code}")

# ============================================================================
# FINAL RESULTS
# ============================================================================
print("\n" + "=" * 80)
print("FINAL TEST RESULTS")
print("=" * 80)

print(f"\n✅ Passed: {test_results['passed']}")
print(f"❌ Failed: {test_results['failed']}")
print(f"📊 Total: {test_results['passed'] + test_results['failed']}")

success_rate = (test_results['passed'] / (test_results['passed'] + test_results['failed'])) * 100
print(f"🎯 Success Rate: {success_rate:.1f}%")

if test_results['failed'] == 0:
    print("\n🎉 ALL TESTS PASSED! Backend is production-ready!")
else:
    print(f"\n⚠️ {test_results['failed']} test(s) failed. Review above for details.")

print("\n" + "=" * 80)
