"""
Repository layer for Circles - handles all database operations.
"""
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.circles.constants import (
    COLLECTION_NAME,
    MAX_MEMBERS_PER_CIRCLE,
    generate_invite_code,
)


class CircleRepository:
    """Repository for circle database operations."""

    def __init__(self, db):
        self.collection = db[COLLECTION_NAME]
        self.posts_collection = db.posts

    # =========================================================================
    # CIRCLE CRUD OPERATIONS
    # =========================================================================

    async def create(self, circle_data: dict) -> dict:
        """
        Create a new circle.

        Args:
            circle_data: Circle document to insert

        Returns:
            Created circle document with _id
        """
        result = await self.collection.insert_one(circle_data)
        return await self.collection.find_one({"_id": result.inserted_id})

    async def find_by_id(self, circle_id: str) -> Optional[dict]:
        """
        Find a circle by its ID.

        Args:
            circle_id: Circle ObjectId as string

        Returns:
            Circle document or None
        """
        if not ObjectId.is_valid(circle_id):
            return None
        return await self.collection.find_one({"_id": ObjectId(circle_id)})

    async def find_by_invite_code(self, invite_code: str) -> Optional[dict]:
        """
        Find a circle by its invite code.

        Args:
            invite_code: 8-character invite code (case-insensitive)

        Returns:
            Circle document or None
        """
        return await self.collection.find_one({
            "invite_code": invite_code.upper()
        })

    async def find_by_member(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[dict]:
        """
        Find all circles where user is a member.

        Args:
            user_id: User ID to search for
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of circle documents
        """
        cursor = self.collection.find({
            "members.user_id": user_id
        }).sort("created_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def count_by_member(self, user_id: str) -> int:
        """
        Count circles where user is a member.

        Args:
            user_id: User ID to count for

        Returns:
            Number of circles
        """
        return await self.collection.count_documents({
            "members.user_id": user_id
        })

    async def update(self, circle_id: str, update_data: dict) -> Optional[dict]:
        """
        Update a circle.

        Args:
            circle_id: Circle ID to update
            update_data: Fields to update

        Returns:
            Updated circle document or None
        """
        if not ObjectId.is_valid(circle_id):
            return None

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(circle_id)},
            {"$set": update_data},
            return_document=True
        )
        return result

    async def delete(self, circle_id: str) -> bool:
        """
        Delete a circle.

        Args:
            circle_id: Circle ID to delete

        Returns:
            True if deleted, False otherwise
        """
        if not ObjectId.is_valid(circle_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(circle_id)})
        return result.deleted_count > 0

    # =========================================================================
    # MEMBERSHIP OPERATIONS
    # =========================================================================

    async def find_by_id_and_member(
        self,
        circle_id: str,
        user_id: str
    ) -> Optional[dict]:
        """
        Find a circle by ID only if user is a member.
        This is the primary security check for circle access.

        Args:
            circle_id: Circle ID
            user_id: User ID to verify membership

        Returns:
            Circle document if user is member, None otherwise
        """
        if not ObjectId.is_valid(circle_id):
            return None

        return await self.collection.find_one({
            "_id": ObjectId(circle_id),
            "members.user_id": user_id
        })

    async def is_member(self, circle_id: str, user_id: str) -> bool:
        """
        Check if user is a member of a circle.

        Args:
            circle_id: Circle ID
            user_id: User ID to check

        Returns:
            True if member, False otherwise
        """
        circle = await self.find_by_id_and_member(circle_id, user_id)
        return circle is not None

    async def add_member(
        self,
        circle_id: str,
        user_id: str,
        username: str
    ) -> Optional[dict]:
        """
        Add a member to a circle atomically.
        Only succeeds if circle is not full and user is not already a member.

        Args:
            circle_id: Circle ID
            user_id: User ID to add
            username: Username to add

        Returns:
            Updated circle document or None if failed
        """
        if not ObjectId.is_valid(circle_id):
            return None

        new_member = {
            "user_id": user_id,
            "username": username,
            "joined_at": datetime.utcnow()
        }

        # Atomic update: only if not full and user not already member
        result = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(circle_id),
                "member_count": {"$lt": MAX_MEMBERS_PER_CIRCLE},
                "members.user_id": {"$ne": user_id}  # Not already a member
            },
            {
                "$push": {"members": new_member},
                "$inc": {"member_count": 1}
            },
            return_document=True
        )
        return result

    async def remove_member(self, circle_id: str, user_id: str) -> Optional[dict]:
        """
        Remove a member from a circle.
        Note: In our design, members cannot leave. This is for edge cases like
        account deletion.

        Args:
            circle_id: Circle ID
            user_id: User ID to remove

        Returns:
            Updated circle document or None
        """
        if not ObjectId.is_valid(circle_id):
            return None

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(circle_id)},
            {
                "$pull": {"members": {"user_id": user_id}},
                "$inc": {"member_count": -1}
            },
            return_document=True
        )
        return result

    # =========================================================================
    # INVITE CODE OPERATIONS
    # =========================================================================

    async def regenerate_invite_code(self, circle_id: str) -> Optional[str]:
        """
        Generate a new unique invite code for a circle.

        Args:
            circle_id: Circle ID

        Returns:
            New invite code or None if failed
        """
        if not ObjectId.is_valid(circle_id):
            return None

        # Generate new code and ensure uniqueness
        max_attempts = 10
        for _ in range(max_attempts):
            new_code = generate_invite_code()

            # Check if code is already in use
            existing = await self.collection.find_one({"invite_code": new_code})
            if existing is None:
                # Update the circle with new code
                result = await self.collection.find_one_and_update(
                    {"_id": ObjectId(circle_id)},
                    {"$set": {"invite_code": new_code}},
                    return_document=True
                )
                if result:
                    return new_code

        return None  # Failed to generate unique code

    async def is_invite_code_unique(self, code: str) -> bool:
        """
        Check if an invite code is unique (not already in use).

        Args:
            code: Invite code to check

        Returns:
            True if unique, False if already exists
        """
        existing = await self.collection.find_one({"invite_code": code.upper()})
        return existing is None

    # =========================================================================
    # DELETION VOTE OPERATIONS
    # =========================================================================

    async def add_deletion_vote(self, circle_id: str, user_id: str) -> Optional[dict]:
        """
        Add a user's vote to delete the circle.

        Args:
            circle_id: Circle ID
            user_id: User ID voting

        Returns:
            Updated circle document or None
        """
        if not ObjectId.is_valid(circle_id):
            return None

        # $addToSet ensures no duplicate votes
        result = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(circle_id),
                "members.user_id": user_id  # Must be a member
            },
            {"$addToSet": {"deletion_votes": user_id}},
            return_document=True
        )
        return result

    async def remove_deletion_vote(self, circle_id: str, user_id: str) -> Optional[dict]:
        """
        Remove a user's vote to delete the circle.

        Args:
            circle_id: Circle ID
            user_id: User ID revoking vote

        Returns:
            Updated circle document or None
        """
        if not ObjectId.is_valid(circle_id):
            return None

        result = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(circle_id),
                "members.user_id": user_id  # Must be a member
            },
            {"$pull": {"deletion_votes": user_id}},
            return_document=True
        )
        return result

    # =========================================================================
    # POST-RELATED OPERATIONS
    # =========================================================================

    async def get_last_activity(self, circle_id: str) -> Optional[datetime]:
        """
        Get the timestamp of the most recent post in a circle.

        Args:
            circle_id: Circle ID

        Returns:
            Datetime of last post or None
        """
        post = await self.posts_collection.find_one(
            {"circle_ids": circle_id},
            sort=[("created_at", -1)]
        )
        if post:
            return post.get("created_at")
        return None

    async def orphan_posts_on_delete(self, circle_id: str) -> int:
        """
        When a circle is deleted, update posts to remove the circle_id.
        Posts that were only in this circle become private.

        Args:
            circle_id: Circle ID being deleted

        Returns:
            Number of posts updated
        """
        # Remove this circle_id from all posts
        result = await self.posts_collection.update_many(
            {"circle_ids": circle_id},
            {"$pull": {"circle_ids": circle_id}}
        )

        # Posts with empty circle_ids array should become private
        await self.posts_collection.update_many(
            {
                "visibility": "circles",
                "circle_ids": {"$size": 0}
            },
            {
                "$set": {"visibility": "private"},
                "$unset": {"circle_ids": ""}
            }
        )

        return result.modified_count
