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
