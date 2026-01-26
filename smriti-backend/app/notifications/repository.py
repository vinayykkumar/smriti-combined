from datetime import datetime
from typing import List

class NotificationRepository:
    def __init__(self, db):
        self.collection = db.device_tokens
    
    async def register_token(self, user_id: str, token: str, platform: str):
        """Register or update a device token"""
        await self.collection.update_one(
            {"token": token},
            {
                "$set": {
                    "user_id": user_id,
                    "token": token,
                    "platform": platform,
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    async def remove_token(self, token: str):
        """Remove a device token"""
        await self.collection.delete_one({"token": token})
    
    async def get_all_tokens_except_user(self, exclude_user_id: str) -> List[str]:
        """Get all device tokens except those belonging to a specific user"""
        cursor = self.collection.find(
            {"user_id": {"$ne": exclude_user_id}},
            {"token": 1, "_id": 0}
        )
        tokens = await cursor.to_list(length=None)
        return [t["token"] for t in tokens]

    async def get_tokens_for_user(self, user_id: str) -> List[str]:
        """
        Get all device tokens for a specific user.

        Used by Today's Quote feature to send push to all user's devices.

        Args:
            user_id: User's ObjectId as string

        Returns:
            List of FCM token strings
        """
        cursor = self.collection.find(
            {"user_id": user_id},
            {"token": 1, "_id": 0}
        )
        # Limit to 50 devices per user
        tokens = await cursor.to_list(length=50)
        return [t["token"] for t in tokens if t.get("token")]

    async def get_tokens_for_users(self, user_ids: List[str], exclude_user_id: str = None) -> List[str]:
        """
        Get device tokens for multiple users.

        Used by circle notifications to notify all circle members.

        Args:
            user_ids: List of user IDs to get tokens for
            exclude_user_id: Optional user ID to exclude (e.g., the post author)

        Returns:
            List of FCM token strings
        """
        query = {"user_id": {"$in": user_ids}}
        if exclude_user_id:
            query["user_id"]["$ne"] = exclude_user_id
            # Rebuild query properly
            query = {
                "$and": [
                    {"user_id": {"$in": user_ids}},
                    {"user_id": {"$ne": exclude_user_id}}
                ]
            }

        cursor = self.collection.find(query, {"token": 1, "_id": 0})
        tokens = await cursor.to_list(length=None)
        return [t["token"] for t in tokens if t.get("token")]
