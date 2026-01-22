"""
Repository layer for auth/users - handles all database operations
"""
from typing import Optional

class UserRepository:
    """Repository for user database operations"""
    
    def __init__(self, db):
        self.collection = db.users
    
    async def find_by_username(self, username: str) -> Optional[dict]:
        """Find user by username"""
        return await self.collection.find_one({"username": username})
    
    async def find_by_email(self, email: str) -> Optional[dict]:
        """Find user by email"""
        if not email:
            return None
        return await self.collection.find_one({"email": email})
    
    async def find_by_phone(self, phone: str) -> Optional[dict]:
        """Find user by phone"""
        if not phone:
            return None
        return await self.collection.find_one({"phone": phone})
    
    async def create(self, user_data: dict) -> dict:
        """Create a new user"""
        result = await self.collection.insert_one(user_data)
        return await self.collection.find_one({"_id": result.inserted_id})
