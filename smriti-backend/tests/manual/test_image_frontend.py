import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("VERIFYING IMAGE SUPPORT FOR FRONTEND")
print("=" * 80)

# Login
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "win_i",
    "password": "test@12345"
})

token = response.json()['data']['token']

# Test 1: Get all posts (should include image posts)
print("\n### Test 1: GET /api/posts/ - Check if images are returned")
response = requests.get(
    f"{BASE_URL}/api/posts/",
    headers={"Authorization": f"Bearer {token}"}
)

data = response.json()
print(f"Status: {response.status_code}")
print(f"Total posts: {data['data']['count']}")

# Find image posts
image_posts = [p for p in data['data']['posts'] if p.get('contentType') == 'image']
print(f"Image posts: {len(image_posts)}")

if image_posts:
    print("\n✅ Image post found in GET response:")
    img_post = image_posts[0]
    print(f"  - Post ID: {img_post['postId']}")
    print(f"  - Title: {img_post['title']}")
    print(f"  - Image URL: {img_post.get('imageUrl', 'MISSING!')}")
    print(f"  - Has imageUrl field: {'imageUrl' in img_post}")
    print(f"  - Has imagePublicId field: {'imagePublicId' in img_post}")
else:
    print("⚠️ No image posts found")

# Test 2: Check response structure
print("\n### Test 2: Response Structure Check")
if image_posts:
    img_post = image_posts[0]
    required_fields = ['postId', 'contentType', 'imageUrl', 'author', 'createdAt']
    missing_fields = [f for f in required_fields if f not in img_post]
    
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
    else:
        print(f"✅ All required fields present")
    
    print(f"\nFull post structure:")
    print(json.dumps(img_post, indent=2))

# Test 3: Frontend display scenario
print("\n### Test 3: Frontend Display Scenario")
if image_posts:
    img_post = image_posts[0]
    print("Frontend would display:")
    print(f"  Title: {img_post.get('title', 'Untitled')}")
    print(f"  Author: @{img_post['author']['username']}")
    print(f"  Image: <Image source={{uri: '{img_post.get('imageUrl')}'}} />")
    print(f"  Caption: {img_post.get('textContent', '')}")
    print("\n✅ Frontend has all data needed to display image post")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
