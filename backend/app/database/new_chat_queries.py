"""
Chat CRUD operations for MongoDB
"""
from typing import List, Optional
from datetime import datetime
from app.database.mongo_db import get_collection
from app.database.schemas import Chat, Message
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def create_chat(chat_data: Chat) -> Chat:
    """
    Create a new chat
    
    Args:
        chat_data: Chat object to create
        
    Returns:
        Created chat
    """
    collection = get_collection("chats")
    chat_dict = chat_data.model_dump()
    result = await collection.insert_one(chat_dict)
    logger.info(f"Created chat: {chat_data.id}")
    return chat_data


async def get_chat_by_id(chat_id: str) -> Optional[Chat]:
    """
    Get chat by ID
    
    Args:
        chat_id: ID of the chat
        
    Returns:
        Chat object or None
    """
    collection = get_collection("chats")
    chat_doc = await collection.find_one({"id": chat_id})
    
    if chat_doc:
        chat_doc.pop("_id", None)
        return Chat(**chat_doc)
    return None


async def get_all_chats() -> List[Chat]:
    """
    Get all chats
    
    Returns:
        List of chats
    """
    collection = get_collection("chats")
    cursor = collection.find({}).sort("updated_at", -1)
    chats = []
    
    async for doc in cursor:
        doc.pop("_id", None)
        chats.append(Chat(**doc))
    
    return chats


async def add_message_to_chat(chat_id: str, message: Message) -> Optional[Chat]:
    """
    Add a message to a chat
    
    Args:
        chat_id: ID of the chat
        message: Message to add
        
    Returns:
        Updated chat or None
    """
    collection = get_collection("chats")
    
    result = await collection.update_one(
        {"id": chat_id},
        {
            "$push": {"messages": message.model_dump()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count > 0:
        logger.info(f"Added message to chat: {chat_id}")
        return await get_chat_by_id(chat_id)
    
    return None


async def update_chat(chat_id: str, update_data: dict) -> Optional[Chat]:
    """
    Update a chat
    
    Args:
        chat_id: ID of the chat to update
        update_data: Dictionary with fields to update
        
    Returns:
        Updated chat or None
    """
    collection = get_collection("chats")
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    result = await collection.update_one(
        {"id": chat_id},
        {"$set": update_data}
    )
    
    if result.modified_count > 0:
        logger.info(f"Updated chat: {chat_id}")
        return await get_chat_by_id(chat_id)
    
    return None


async def delete_chat(chat_id: str) -> bool:
    """
    Delete a chat
    
    Args:
        chat_id: ID of the chat to delete
        
    Returns:
        True if deleted, False otherwise
    """
    collection = get_collection("chats")
    result = await collection.delete_one({"id": chat_id})
    
    if result.deleted_count > 0:
        logger.info(f"Deleted chat: {chat_id}")
        return True
    
    return False


async def get_chat_messages(chat_id: str) -> List[Message]:
    """
    Get all messages from a chat
    
    Args:
        chat_id: ID of the chat
        
    Returns:
        List of messages
    """
    chat = await get_chat_by_id(chat_id)
    if chat:
        return chat.messages
    return []
