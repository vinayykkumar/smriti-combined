"""
Repository layer for posts - handles all database operations
"""
from bson import ObjectId
from typing import List, Optional

class PostRepository:
    """Repository for post database operations"""
    
    def __init__(self, db):
        self.collection = db.posts
    
    async def find_all(self, skip: int, limit: int) -> List[dict]:
        """Get all posts with pagination"""
        cursor = self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_user(self, user_id: str, skip: int, limit: int) -> List[dict]:
        """Get posts by specific user"""
        cursor = self.collection.find({"author.user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def find_by_id(self, post_id: str) -> Optional[dict]:
        """Get post by ID"""
        if not ObjectId.is_valid(post_id):
            return None
        return await self.collection.find_one({"_id": ObjectId(post_id)})
    
    async def create(self, post_data: dict) -> dict:
        """Create a new post"""
        result = await self.collection.insert_one(post_data)
        return await self.collection.find_one({"_id": result.inserted_id})
    
    async def delete(self, post_id: str) -> bool:
        """Delete a post by ID"""
        result = await self.collection.delete_one({"_id": ObjectId(post_id)})
        return result.deleted_count > 0
    
    async def count_by_user(self, user_id: str) -> int:
        """Count posts by user"""
        return await self.collection.count_documents({"author.user_id": user_id})
