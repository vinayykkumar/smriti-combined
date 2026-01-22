from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    
    def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=60000,
            connectTimeoutMS=60000,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        logger.info(
            "Connected to MongoDB",
            extra={"database": settings.DATABASE_NAME}
        )
        
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")
            
    def get_db(self):
        """Get database instance"""
        return self.client[settings.DATABASE_NAME]

db = Database()

async def get_database():
    return db.get_db()
