"""Chat-related data models"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)
    
    def __repr__(self):
        return f"ObjectId('{self}')'"


class Message(BaseModel):
    """Single message in a conversation"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Hello, how can you help?",
                "timestamp": "2024-01-20T10:30:00"
            }
        }


class MessageCreate(BaseModel):
    """Request model for creating a message"""
    role: str
    content: str


class Conversation(BaseModel):
    """Conversation document model"""
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: str
    title: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "title": "Python Help",
                "messages": [
                    {"role": "user", "content": "How do I read a file?"},
                    {"role": "assistant", "content": "You can use the open() function..."}
                ]
            }
        }
        populate_by_name = True


class ConversationCreate(BaseModel):
    """Request model for creating a conversation"""
    title: Optional[str] = None
    metadata: Optional[dict] = None


class ConversationUpdate(BaseModel):
    """Request model for updating a conversation"""
    title: Optional[str] = None
    metadata: Optional[dict] = None


class ConversationResponse(BaseModel):
    """Response model for conversation"""
    id: str = Field(alias="_id")
    user_id: str
    title: Optional[str]
    message_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
