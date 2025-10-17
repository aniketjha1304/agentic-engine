"""
Models for request and response schemas for chat APIs.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime


# Request Schemas
class CreateChatRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user creating the chat.")
    title: str = Field(..., description="Title of the chat.")
    chat_id: str = Field(..., description="Id of the chat.")


class PostMessageRequest(BaseModel):
    role: str = Field(..., description="Role of the sender (e.g., 'user' or 'system').")
    content: Any = Field(..., description="Message content in JSON format or string.")


# Response Schemas
class ChatResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the chat.")
    created_at: datetime = Field(
        ..., description="Timestamp when the chat was created."
    )
    title: str = Field(..., description="Title of the chat.")


class MessageResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the message.")
    chat_id: UUID = Field(..., description="Unique identifier of the associated chat.")
    role: str = Field(..., description="Role of the sender.")
    content: Any = Field(..., description="Message content in JSON format.")
    created_at: datetime = Field(
        ..., description="Timestamp when the message was created."
    )


class GetChatsResponse(BaseModel):
    chats: List[ChatResponse] = Field(..., description="List of chats for the user.")


class GetMessagesResponse(BaseModel):
    messages: List[MessageResponse] = Field(
        ..., description="List of messages in the chat."
    )


class CreateChatResponse(BaseModel):
    message: str = Field(..., description="Result message for chat creation.")
    chatId: UUID = Field(..., description="Unique identifier of the created chat.")


class PostMessageResponse(BaseModel):
    message: str = Field(..., description="Result message for posting a message.")
    messageId: UUID = Field(
        ..., description="Unique identifier of the created message."
    )


class DeleteMessageResponse(BaseModel):
    message: str = Field(..., description="Result message for Message deletion.")


class DeleteChatResponse(BaseModel):
    message: str = Field(..., description="Result message for chat deletion.")


class ChatResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the chat.")
    createdAt: datetime = Field(..., description="Timestamp when the chat was created.")
    title: str = Field(..., description="Title of the chat.")
    userId: int = Field(..., description="Unique identifier for the chat.")
