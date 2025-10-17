from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from app.utils.api_key_required import api_key_required
from uuid import UUID
from app.database.chat_queries import (
    save_chat,
    save_message,
    delete_chat_by_id,
    get_chats_by_user_id,
    get_messages_by_chat_id,
    get_chat_by_id,
    get_message_by_id,
    delete_messages_after_timestamp,
)
from app.api_models.chat import (
    CreateChatRequest,
    PostMessageRequest,
    GetChatsResponse,
    GetMessagesResponse,
    CreateChatResponse,
    PostMessageResponse,
    DeleteChatResponse,
    DeleteMessageResponse,
    ChatResponse,
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chats/",
    dependencies=[Depends(api_key_required)],
    response_model=CreateChatResponse,
    summary="Create a new chat",
    description="Endpoint to create a new chat for a user.",
)
async def create_chat(request: CreateChatRequest):
    """
    Creates a new chat for the specified user with the given title.
    """
    try:
        chat_id = await save_chat(
            user_id=request.user_id, title=request.title, chat_id=request.chat_id
        )
        return CreateChatResponse(message="Chat created successfully", chatId=chat_id)
    except Exception as e:
        logger.error(f"Error while creating chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/chats/{chat_id}/messages",
    dependencies=[Depends(api_key_required)],
    response_model=PostMessageResponse,
    summary="Post a message to a chat",
    description="Endpoint to post a message to a specific chat.",
)
async def post_message(chat_id: UUID, request: PostMessageRequest):
    """
    Posts a new message to a specific chat.
    """
    try:
        message_id = await save_message(
            chat_id=chat_id, role=request.role, content=request.content
        )
        return PostMessageResponse(
            message="Message posted successfully", messageId=message_id
        )
    except Exception as e:
        logger.error(f"Error while saving message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/chats/{chat_id}",
    dependencies=[Depends(api_key_required)],
    response_model=DeleteChatResponse,
    summary="Delete a chat and its messages",
    description="Endpoint to delete a chat along with its messages.",
)
async def delete_chat(chat_id: UUID):
    """
    Deletes a chat and all its associated messages.
    """
    try:
        await delete_chat_by_id(chat_id=chat_id)
        return DeleteChatResponse(message="Chat and its messages deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/users/{user_id}/chats",
    dependencies=[Depends(api_key_required)],
    response_model=GetChatsResponse,
    summary="Get all chats for a user",
    description="Endpoint to retrieve all chats for a specific user.",
)
async def get_chats(user_id: int):
    """
    Retrieves all chats associated with a specific user.
    """
    try:
        chats = await get_chats_by_user_id(user_id=user_id)
        return GetChatsResponse(chats=chats)
    except Exception as e:
        logger.error(f"Error while getting chats for user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/chats/{chat_id}/messages",
    dependencies=[Depends(api_key_required)],
    response_model=GetMessagesResponse,
    summary="Get all messages for a chat",
    description="Endpoint to retrieve all messages from a specific chat.",
)
async def get_messages(chat_id: UUID):
    """
    Retrieves all messages associated with a specific chat.
    """
    try:
        messages = await get_messages_by_chat_id(chat_id=chat_id)
        return GetMessagesResponse(messages=messages)
    except Exception as e:
        logger.error(f"Error while getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# TODO: Implement the schema here
@router.get(
    "/chats/{chat_id}",
    dependencies=[Depends(api_key_required)],
    summary="Get chat details by ID",
    description="Endpoint to retrieve details of a specific chat by its ID.",
)
async def get_chat_details(chat_id: UUID):
    """
    Retrieves details of a specific chat by its ID.
    """

    try:
        chat_data = await get_chat_by_id(chat_id=chat_id)
        if chat_data is not None:
            return ChatResponse(
                title=chat_data["title"],
                id=chat_data["id"],
                createdAt=chat_data["created_at"],
                userId=chat_data["user_id"],
            )
        return chat_data
    except Exception as e:
        logger.error(f"Error while getting chat details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/messages/{message_id}",
    dependencies=[Depends(api_key_required)],
    summary="Get message details by ID",
    description="Endpoint to retrieve details of a specific message by its ID.",
)
async def get_message_details(message_id: UUID):
    """
    Retrieves details of a specific chat by its ID.
    """
    query = """
        SELECT id, created_at, user_id, title
        FROM chat
        WHERE id = :chat_id
    """

    try:
        message_data = await get_message_by_id(message_id=message_id)
        return message_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/chats/{chat_id}/messages",
    dependencies=[Depends(api_key_required)],
    response_model=DeleteMessageResponse,
    summary="Delete messages by chat ID after a timestamp",
    description="Endpoint to delete messages from a specific chat after a given timestamp.",
)
async def delete_messages_by_timestamp(chat_id: UUID, timestamp: datetime):
    """
    Deletes all messages from a specific chat that were created after the given timestamp.
    """
    try:
        rows_deleted = await delete_messages_after_timestamp(
            chat_id=chat_id, timestamp=timestamp
        )
        # if rows_deleted == 0:
        #     raise HTTPException(status_code=404, detail="No messages found to delete")
        return DeleteMessageResponse(
            message=f"Deleted {rows_deleted} messages successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
