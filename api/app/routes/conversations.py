"""Conversation endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection
from bson.objectid import ObjectId
from datetime import datetime
from app.db.mongodb import get_mongodb
from app.models.chat import (
    Conversation, ConversationCreate, ConversationUpdate,
    ConversationResponse, Message, MessageCreate
)
from typing import List

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=Conversation, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    user_id: str,
    conversation: ConversationCreate,
    db = Depends(get_mongodb)
):
    """Create a new conversation"""
    conv_data = {
        "user_id": user_id,
        "title": conversation.title or "Untitled Conversation",
        "messages": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "metadata": conversation.metadata or {}
    }
    
    result = db.conversations.insert_one(conv_data)
    conv_data["_id"] = result.inserted_id
    return conv_data


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    user_id: str,
    db = Depends(get_mongodb)
):
    """Get a specific conversation"""
    try:
        obj_id = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    conversation = db.conversations.find_one({
        "_id": obj_id,
        "user_id": user_id
    })
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: str,
    limit: int = 50,
    skip: int = 0,
    db = Depends(get_mongodb)
):
    """List all conversations for a user"""
    conversations = db.conversations.find(
        {"user_id": user_id}
    ).sort("updated_at", -1).skip(skip).limit(limit)
    
    return [
        {
            "_id": str(conv["_id"]),
            "user_id": conv["user_id"],
            "title": conv.get("title"),
            "message_count": len(conv.get("messages", [])),
            "created_at": conv["created_at"],
            "updated_at": conv["updated_at"]
        }
        for conv in conversations
    ]


@router.put("/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: str,
    user_id: str,
    updates: ConversationUpdate,
    db = Depends(get_mongodb)
):
    """Update a conversation"""
    try:
        obj_id = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    update_data = {
        k: v for k, v in updates.dict().items() if v is not None
    }
    update_data["updated_at"] = datetime.utcnow()
    
    result = db.conversations.find_one_and_update(
        {"_id": obj_id, "user_id": user_id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return result


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    user_id: str,
    db = Depends(get_mongodb)
):
    """Delete a conversation"""
    try:
        obj_id = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    result = db.conversations.delete_one({
        "_id": obj_id,
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("/{conversation_id}/messages", response_model=Message)
async def add_message(
    conversation_id: str,
    user_id: str,
    message: MessageCreate,
    db = Depends(get_mongodb)
):
    """Add a message to a conversation"""
    try:
        obj_id = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    msg_data = {
        "role": message.role,
        "content": message.content,
        "timestamp": datetime.utcnow()
    }
    
    result = db.conversations.find_one_and_update(
        {"_id": obj_id, "user_id": user_id},
        {
            "$push": {"messages": msg_data},
            "$set": {"updated_at": datetime.utcnow()}
        },
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return msg_data


@router.get("/{conversation_id}/messages", response_model=List[Message])
async def get_messages(
    conversation_id: str,
    user_id: str,
    db = Depends(get_mongodb)
):
    """Get all messages from a conversation"""
    try:
        obj_id = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    conversation = db.conversations.find_one({
        "_id": obj_id,
        "user_id": user_id
    })
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation.get("messages", [])
