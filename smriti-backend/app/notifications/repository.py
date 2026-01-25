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
