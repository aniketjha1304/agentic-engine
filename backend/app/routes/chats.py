"""
Chat API routes for CRUD operations
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.database.schemas import Chat, CreateChatRequest
from app.database.new_chat_queries import (
    create_chat,
    get_chat_by_id,
    get_all_chats,
    update_chat,
    delete_chat,
    get_chat_messages,
)
from app.utils.api_key_required import api_key_required
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/chats",
    dependencies=[Depends(api_key_required)],
    response_model=Chat,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat",
    description="Create a new chat session",
)
async def create_new_chat(request: CreateChatRequest):
    """
    Create a new chat
    """
    try:
        chat = Chat(name=request.name, agent_name=request.agent_name)
        created_chat = await create_chat(chat)
        return created_chat
    except Exception as e:
        logger.error(f"Error creating chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create chat")


@router.get(
    "/chats",
    dependencies=[Depends(api_key_required)],
    response_model=List[Chat],
    summary="Get all chats",
    description="Retrieve list of all chats",
)
async def list_chats():
    """
    Get all chats
    """
    try:
        chats = await get_all_chats()
        return chats
    except Exception as e:
        logger.error(f"Error fetching chats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chats")


@router.get(
    "/chats/{chat_id}",
    dependencies=[Depends(api_key_required)],
    response_model=Chat,
    summary="Get chat by ID",
    description="Retrieve a specific chat with all messages",
)
async def get_chat(chat_id: str):
    """
    Get chat by ID
    """
    try:
        chat = await get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail=f"Chat '{chat_id}' not found")
        return chat
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat")


@router.put(
    "/chats/{chat_id}",
    dependencies=[Depends(api_key_required)],
    response_model=Chat,
    summary="Update a chat",
    description="Update chat name or agent association",
)
async def update_existing_chat(chat_id: str, name: str = None, agent_name: str = None):
    """
    Update a chat
    """
    try:
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if agent_name is not None:
            update_data["agent_name"] = agent_name

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        updated_chat = await update_chat(chat_id, update_data)
        if not updated_chat:
            raise HTTPException(status_code=404, detail=f"Chat '{chat_id}' not found")

        return updated_chat
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update chat")


@router.delete(
    "/chats/{chat_id}",
    dependencies=[Depends(api_key_required)],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat",
    description="Delete a chat by ID",
)
async def delete_existing_chat(chat_id: str):
    """
    Delete a chat
    """
    try:
        deleted = await delete_chat(chat_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Chat '{chat_id}' not found")
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete chat")
