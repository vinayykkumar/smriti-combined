"""
Database initialization script
Creates indexes for better query performance
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.quotes.constants import COLLECTION_NAME as QUOTES_COLLECTION


async def create_indexes():
    """Create database indexes"""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]

    # =========================================================================
    # USERS COLLECTION INDEXES
    # =========================================================================
    await db.users.create_index("username", unique=True)
    await db.users.create_index("created_at")
    print("  ✓ Users indexes created")

    # =========================================================================
    # POSTS COLLECTION INDEXES
    # =========================================================================
    await db.posts.create_index([("created_at", -1)])  # For chronological sorting
    await db.posts.create_index("author.user_id")
    await db.posts.create_index("content_type")

    # Text index for full-text search on title and text_content
    await db.posts.create_index(
        [("title", "text"), ("text_content", "text")],
        name="posts_text_search_index",
        default_language="english"
    )

    # Circles-related indexes for posts
    await db.posts.create_index("visibility")  # Filter public vs circles posts
    await db.posts.create_index("circle_ids")  # Find posts in a circle
    await db.posts.create_index([("circle_ids", 1), ("created_at", -1)])  # Circle feed query
    print("  ✓ Posts indexes created")

    # =========================================================================
    # CIRCLES COLLECTION INDEXES
    # =========================================================================
    await db.circles.create_index("invite_code", unique=True)  # Unique invite codes
    await db.circles.create_index("members.user_id")  # Find circles by member
    await db.circles.create_index([("members.user_id", 1), ("created_at", -1)])  # User's circles sorted
    print("  ✓ Circles indexes created")

    # =========================================================================
    # USER_DAILY_QUOTES COLLECTION INDEXES (Today's Quote feature)
    # =========================================================================

    # Index 1: Unique constraint - one record per user per day
    # Used for: Primary lookups, preventing duplicate records
    await db[QUOTES_COLLECTION].create_index(
        [("user_id", 1), ("day_key", -1)],
        unique=True,
        name="user_day_unique"
    )

    # Index 2: For cron job query (find pending pushes)
    # Used for: POST /api/internal/daily-quote-push
    # Query: push_sent = false AND scheduled_push_time_utc <= now
    await db[QUOTES_COLLECTION].create_index(
        [("push_sent", 1), ("scheduled_push_time_utc", 1)],
        name="pending_push_lookup"
    )

    # Index 3: For history query (user's past quotes, sorted by day)
    # Used for: GET /api/quotes/history
    # Query: user_id = X AND push_sent = true, sorted by day_key desc
    await db[QUOTES_COLLECTION].create_index(
        [("user_id", 1), ("push_sent", 1), ("day_key", -1)],
        name="user_history_lookup"
    )
    print("  ✓ User daily quotes indexes created")

    # =========================================================================
    # DEVICE TOKENS COLLECTION INDEXES
    # =========================================================================
    # Check if device_tokens index exists, create if not
    existing_indexes = await db.device_tokens.index_information()
    if "user_id_1" not in existing_indexes:
        await db.device_tokens.create_index("user_id")
    if "token_1" not in existing_indexes:
        await db.device_tokens.create_index("token", unique=True)
    # Composite index for efficient queries by user sorted by time
    if "user_id_1_created_at_-1" not in existing_indexes:
        await db.device_tokens.create_index([("user_id", 1), ("created_at", -1)])
    print("  ✓ Device tokens indexes verified")

    print("\n✅ All database indexes created successfully")
    client.close()


async def create_quotes_indexes_only():
    """Create only the quotes collection indexes (for incremental updates)"""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]

    await db[QUOTES_COLLECTION].create_index(
        [("user_id", 1), ("day_key", -1)],
        unique=True,
        name="user_day_unique"
    )

    await db[QUOTES_COLLECTION].create_index(
        [("push_sent", 1), ("scheduled_push_time_utc", 1)],
        name="pending_push_lookup"
    )

    await db[QUOTES_COLLECTION].create_index(
        [("user_id", 1), ("push_sent", 1), ("day_key", -1)],
        name="user_history_lookup"
    )

    print("✅ Quotes indexes created successfully")
    client.close()


if __name__ == "__main__":
    import asyncio
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--quotes-only":
        asyncio.run(create_quotes_indexes_only())
    else:
        asyncio.run(create_indexes())
