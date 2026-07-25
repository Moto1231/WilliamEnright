"""MongoDB connection and utilities"""
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from app.config import get_settings
from typing import Optional


class MongoDB:
    """MongoDB connection manager"""
    
    _client: Optional[MongoClient] = None
    _db = None
    
    @classmethod
    def connect_db(cls):
        """Connect to MongoDB"""
        settings = get_settings()
        try:
            cls._client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
            # Verify connection
            cls._client.admin.command('ping')
            cls._db = cls._client[settings.mongodb_db_name]
            print("✓ Connected to MongoDB")
            return cls._db
        except ServerSelectionTimeoutError:
            print("✗ Failed to connect to MongoDB")
            raise
    
    @classmethod
    def close_db(cls):
        """Close MongoDB connection"""
        if cls._client:
            cls._client.close()
            print("✓ Disconnected from MongoDB")
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls._db is None:
            cls.connect_db()
        return cls._db
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get collection instance"""
        db = cls.get_db()
        return db[collection_name]


def get_mongodb():
    """Dependency for FastAPI to get MongoDB instance"""
    return MongoDB.get_db()
