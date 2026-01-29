"""
Repository layer for companion module - handles all database operations.

Manages:
- User companion settings (stored in users collection)
- Conversation history (stored in companion_history collection)
"""

from bson import ObjectId
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import logging

from app.companion.schemas import (
    CompanionSettings,
    CompanionSettingsUpdate,
    ConversationEntry,
    ConversationEntryCreate
)

logger = logging.getLogger(__name__)


class CompanionRepository:
    """Repository for companion database operations"""

    def __init__(self, db):
        self.db = db
        self.users_collection = db.users
        self.history_collection = db.companion_history

    # ============ Settings Operations ============

    async def get_settings(self, user_id: str) -> Optional[CompanionSettings]:
        """
        Get companion settings for a user.

        Args:
            user_id: User's ID

        Returns:
            CompanionSettings or None if not found
        """
        user = await self.users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {"companion_settings": 1}
        )

        if user and "companion_settings" in user:
            return CompanionSettings(**user["companion_settings"])
        return None

    async def create_default_settings(self, user_id: str) -> CompanionSettings:
        """
        Create default companion settings for a user.

        Args:
            user_id: User's ID

        Returns:
            Created CompanionSettings
        """
        now = datetime.now(timezone.utc)
        default_settings = CompanionSettings(
            created_at=now,
            updated_at=now
        )

        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"companion_settings": default_settings.model_dump()}}
        )

        logger.debug(f"Created default companion settings for user {user_id}")
        return default_settings

    async def update_settings(
        self,
        user_id: str,
        update: CompanionSettingsUpdate
    ) -> CompanionSettings:
        """
        Update companion settings for a user.

        Args:
            user_id: User's ID
            update: Partial settings update

        Returns:
            Updated CompanionSettings
        """
        # Ensure settings exist
        current = await self.get_settings(user_id)
        if not current:
            await self.create_default_settings(user_id)

        # Build update dict (only non-None values)
        update_dict = update.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.get_settings(user_id)

        update_dict["updated_at"] = datetime.now(timezone.utc)

        # Apply updates
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {f"companion_settings.{k}": v for k, v in update_dict.items()}}
        )

        logger.debug(f"Updated companion settings for user {user_id}: {list(update_dict.keys())}")
        return await self.get_settings(user_id)

    async def get_opt_in_status(self, user_id: str) -> bool:
        """
        Quick check if user has opted in to reflection analysis.

        Args:
            user_id: User's ID

        Returns:
            True if opted in, False otherwise
        """
        user = await self.users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {"companion_settings.opt_in_reflection_analysis": 1}
        )

        if user and "companion_settings" in user:
            return user["companion_settings"].get("opt_in_reflection_analysis", False)
        return False

    # ============ Conversation History Operations ============

    async def add_history_entry(
        self,
        entry: ConversationEntryCreate
    ) -> ConversationEntry:
        """
        Add a new conversation history entry.

        Args:
            entry: Entry data to create

        Returns:
            Created ConversationEntry
        """
        doc = {
            "user_id": entry.user_id,
            "type": entry.type,
            "request": entry.request,
            "response": entry.response,
            "created_at": datetime.now(timezone.utc)
        }

        result = await self.history_collection.insert_one(doc)
        doc["_id"] = result.inserted_id

        logger.debug(f"Added history entry for user {entry.user_id}: {entry.type}")

        return ConversationEntry(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            type=doc["type"],
            request=doc["request"],
            response=doc["response"],
            created_at=doc["created_at"]
        )

    async def get_history(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        entry_type: Optional[str] = None
    ) -> tuple[List[ConversationEntry], int]:
        """
        Get paginated conversation history for a user.

        Args:
            user_id: User's ID
            page: Page number (1-indexed)
            limit: Entries per page
            entry_type: Optional filter by type

        Returns:
            Tuple of (entries list, total count)
        """
        # Build query
        query = {"user_id": user_id}
        if entry_type:
            query["type"] = entry_type

        # Get total count
        total = await self.history_collection.count_documents(query)

        # Get paginated entries
        skip = (page - 1) * limit
        cursor = self.history_collection.find(query) \
            .sort("created_at", -1) \
            .skip(skip) \
            .limit(limit)

        entries = []
        async for doc in cursor:
            entries.append(ConversationEntry(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
                type=doc["type"],
                request=doc["request"],
                response=doc["response"],
                created_at=doc["created_at"]
            ))

        return entries, total

    async def get_history_entry(
        self,
        entry_id: str,
        user_id: str
    ) -> Optional[ConversationEntry]:
        """
        Get a specific history entry (with user ownership check).

        Args:
            entry_id: Entry ID
            user_id: User's ID (for ownership verification)

        Returns:
            ConversationEntry or None
        """
        if not ObjectId.is_valid(entry_id):
            return None

        doc = await self.history_collection.find_one({
            "_id": ObjectId(entry_id),
            "user_id": user_id
        })

        if not doc:
            return None

        return ConversationEntry(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            type=doc["type"],
            request=doc["request"],
            response=doc["response"],
            created_at=doc["created_at"]
        )

    async def delete_history_entry(
        self,
        entry_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a specific history entry (with user ownership check).

        Args:
            entry_id: Entry ID
            user_id: User's ID

        Returns:
            True if deleted, False if not found
        """
        if not ObjectId.is_valid(entry_id):
            return False

        result = await self.history_collection.delete_one({
            "_id": ObjectId(entry_id),
            "user_id": user_id
        })

        if result.deleted_count > 0:
            logger.debug(f"Deleted history entry {entry_id} for user {user_id}")
            return True
        return False

    async def delete_all_history(self, user_id: str) -> int:
        """
        Delete all conversation history for a user.

        Args:
            user_id: User's ID

        Returns:
            Number of entries deleted
        """
        result = await self.history_collection.delete_many({"user_id": user_id})
        logger.info(f"Deleted {result.deleted_count} history entries for user {user_id}")
        return result.deleted_count

    async def cleanup_old_history(self, retention_days: int = 30) -> int:
        """
        Delete history entries older than retention period.

        Args:
            retention_days: Number of days to retain

        Returns:
            Number of entries deleted
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

        result = await self.history_collection.delete_many({
            "created_at": {"$lt": cutoff}
        })

        if result.deleted_count > 0:
            logger.info(f"Cleaned up {result.deleted_count} old history entries")

        return result.deleted_count

    async def enforce_max_entries(
        self,
        user_id: str,
        max_entries: int = 200
    ) -> int:
        """
        Enforce maximum entries per user by deleting oldest.

        Args:
            user_id: User's ID
            max_entries: Maximum entries to keep

        Returns:
            Number of entries deleted
        """
        # Count current entries
        count = await self.history_collection.count_documents({"user_id": user_id})

        if count <= max_entries:
            return 0

        # Find entries to delete (oldest first)
        to_delete = count - max_entries
        cursor = self.history_collection.find(
            {"user_id": user_id},
            {"_id": 1}
        ).sort("created_at", 1).limit(to_delete)

        ids_to_delete = [doc["_id"] async for doc in cursor]

        if ids_to_delete:
            result = await self.history_collection.delete_many({
                "_id": {"$in": ids_to_delete}
            })
            logger.debug(f"Enforced max entries for user {user_id}: deleted {result.deleted_count}")
            return result.deleted_count

        return 0

    # ============ User Posts for Context ============

    async def get_user_posts_for_context(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[dict]:
        """
        Get user's recent posts for AI context.

        Args:
            user_id: User's ID
            limit: Maximum posts to fetch

        Returns:
            List of post documents with content
        """
        posts_collection = self.db.posts

        cursor = posts_collection.find(
            {"author.user_id": user_id},
            {"content": 1, "created_at": 1}
        ).sort("created_at", -1).limit(limit)

        return await cursor.to_list(length=limit)
