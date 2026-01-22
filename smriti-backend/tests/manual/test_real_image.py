import requests
from PIL import Image
import io

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("TESTING REAL IMAGE UPLOAD")
print("=" * 80)

# Login first
print("\n### Step 1: Login")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "win_i",
    "password": "test@12345"
})

if response.status_code == 200:
    token = response.json()['data']['token']
    print(f"✅ Login successful")
    
    # Create a real colorful image (200x200 with gradient)
    print("\n### Step 2: Creating a colorful test image...")
    img = Image.new('RGB', (200, 200))
    pixels = img.load()
    
    # Create a gradient
    for i in range(200):
        for j in range(200):
            pixels[i, j] = (i % 256, j % 256, (i + j) % 256)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    print("✅ Created 200x200 colorful gradient image")
    
    # Upload the image
    print("\n### Step 3: Uploading image to Cloudinary...")
    files = {
        'content_type': (None, 'image'),
        'title': (None, 'Beautiful Gradient'),
        'text_content': (None, 'A colorful gradient image created with Python'),
        'image': ('gradient.png', img_bytes.getvalue(), 'image/png')
    }
    
    response = requests.post(
        f"{BASE_URL}/api/posts/",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("\n✅ Image uploaded successfully!")
        print(f"\nPost ID: {data['post']['postId']}")
        print(f"Title: {data['post']['title']}")
        print(f"Image URL: {data['post']['imageUrl']}")
        print(f"\n🌐 You can view the image at:")
        print(f"   {data['post']['imageUrl']}")
        print("\n📋 Copy this URL and paste in your browser to see the uploaded image!")
    else:
        print(f"\n❌ Upload failed")
        print(f"Response: {response.json()}")
        
else:
    print(f"❌ Login failed")
