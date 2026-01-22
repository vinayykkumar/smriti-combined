"""
Script to create the smriti-test database with necessary collections.
This will create the test database in your MongoDB Atlas Cluster0.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def create_test_database():
    """Create smriti-test database with posts and users collections"""
    
    # Get MongoDB URI from environment
    mongodb_uri = os.getenv("MONGODB_URI")
    
    if not mongodb_uri:
        print("[ERROR] MONGODB_URI not found in .env file")
        return
    
    print("[INFO] Connecting to MongoDB Atlas...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(
        mongodb_uri,
        serverSelectionTimeoutMS=60000,
        connectTimeoutMS=60000,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("[SUCCESS] Connected to MongoDB Atlas")
        
        # Get the test database
        test_db = client["smriti-test"]
        
        # Create collections by inserting and then deleting a dummy document
        # This is necessary because MongoDB creates collections on first write
        
        print("\n[INFO] Creating 'users' collection...")
        await test_db.users.insert_one({"_dummy": True})
        await test_db.users.delete_one({"_dummy": True})
        
        # Create indexes for users collection
        await test_db.users.create_index("username", unique=True)
        await test_db.users.create_index("email", unique=True)
        print("[SUCCESS] Created 'users' collection with indexes")
        
        print("\n[INFO] Creating 'posts' collection...")
        await test_db.posts.insert_one({"_dummy": True})
        await test_db.posts.delete_one({"_dummy": True})
        
        # Create indexes for posts collection
        await test_db.posts.create_index("userId")
        await test_db.posts.create_index("createdAt")
        print("[SUCCESS] Created 'posts' collection with indexes")
        
        # List all databases to confirm
        print("\n[INFO] Available databases:")
        db_list = await client.list_database_names()
        for db_name in db_list:
            if db_name not in ["admin", "local"]:
                print(f"  - {db_name}")
        
        # List collections in smriti-test
        print("\n[INFO] Collections in 'smriti-test':")
        collections = await test_db.list_collection_names()
        for coll in collections:
            print(f"  - {coll}")
        
        print("\n[SUCCESS] Test database 'smriti-test' created successfully!")
        print("\n[NEXT STEPS]")
        print("1. Update your .env file:")
        print("   - For production: DATABASE_NAME=smriti")
        print("   - For testing: DATABASE_NAME=smriti-test")
        print("2. Restart your server")
        print("3. Run your tests")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        client.close()
        print("\n[INFO] Disconnected from MongoDB")

if __name__ == "__main__":
    print("=" * 60)
    print("Creating smriti-test Database")
    print("=" * 60)
    asyncio.run(create_test_database())
