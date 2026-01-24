"""
Database initialization script
Creates indexes for better query performance
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

async def create_indexes():
    """Create database indexes"""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]
    
    # Users collection indexes
    await db.users.create_index("username", unique=True)
    await db.users.create_index("created_at")
    
    # Posts collection indexes
    await db.posts.create_index([("created_at", -1)])  # For chronological sorting
    await db.posts.create_index("author.user_id")
    await db.posts.create_index("content_type")

    # Text index for full-text search on title and text_content
    await db.posts.create_index(
        [("title", "text"), ("text_content", "text")],
        name="posts_text_search_index",
        default_language="english"
    )
    
    print("✅ Database indexes created successfully")
    client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_indexes())
