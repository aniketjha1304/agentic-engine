import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import text
from app.database.db_connect import get_chat_db

from app.database.db_connect import get_ai_persona_hub_db, get_chat_db


def serialize_to_json(content):
    # Check if content is already a JSON-serializable object (e.g., dict, list, or str)
    if isinstance(content, (dict, list)):
        return json.dumps(content)  # Serialize dict or list to JSON string
    elif isinstance(content, str):
        try:
            # Check if the string is already valid JSON
            json.loads(content)
            return content  # Return as is if it's valid JSON
        except json.JSONDecodeError:
            return json.dumps(content)  # Serialize the string into JSON
    else:
        # For other data types, serialize them into JSON (e.g., int, float)
        return json.dumps(content)


async def get_user_by_id(user_id: int):
    query = text(
        """
        SELECT email, name FROM "user"
        WHERE id = :user_id
        LIMIT 1
    """
    )
    async with get_ai_persona_hub_db() as db:
        row_dict = None
        result = await db.execute(query, {"user_id": user_id})
        row = result.fetchone()
        if row:
            row_dict = dict(zip(result.keys(), row))
        return row_dict


async def save_chat(user_id: int, title: str, chat_id: str) -> str:
    query = text(
        """
        INSERT INTO chat (id, created_at, user_id, title)
        VALUES (:id, :created_at, :user_id, :title)
        RETURNING id
    """
    )
    params = {
        "id": chat_id,
        "created_at": datetime.now(),
        "user_id": user_id,
        "title": title,
    }

    async with get_chat_db() as db:
        result = await db.execute(query, params)
        await db.commit()
        return result.scalar()


async def save_message(chat_id: uuid.UUID, role: str, content: dict) -> str:
    query = text(
        """
        INSERT INTO message (id, chat_id, role, content, created_at)
        VALUES (:id, :chat_id, :role, :content, :created_at)
        RETURNING id
    """
    )
    message_id = str(uuid.uuid4())
    params = {
        "id": message_id,
        "chat_id": str(chat_id),
        "role": role,
        "content": serialize_to_json(content),  # Ensure content is JSON
        "created_at": datetime.now(),
    }

    async with get_chat_db() as db:
        result = await db.execute(query, params)
        await db.commit()
        return result.scalar()


async def delete_chat_by_id(chat_id: uuid.UUID):
    async with get_chat_db() as db:
        # Delete messages first
        delete_messages_query = text(
            """
            DELETE FROM message WHERE chat_id = :chat_id
        """
        )
        await db.execute(delete_messages_query, {"chat_id": str(chat_id)})
        await db.commit()
        # Delete the chat
        delete_chat_query = text(
            """
            DELETE FROM chat WHERE id = :chat_id
        """
        )
        await db.execute(delete_chat_query, {"chat_id": str(chat_id)})
        await db.commit()


async def get_chats_by_user_id(user_id: int):
    query = text(
        """
        SELECT id, created_at, title FROM chat
        WHERE user_id = :user_id
        ORDER BY created_at DESC
    """
    )
    async with get_chat_db() as db:
        result = await db.execute(query, {"user_id": user_id})
        rows = result.fetchall()
        return [dict(zip(result.keys(), row)) for row in rows]


async def get_chat_by_id(chat_id: uuid.UUID):
    query = text(
        """
        SELECT * FROM chat
        WHERE id = :chat_id
        LIMIT 1
    """
    )
    async with get_chat_db() as db:
        row_dict = None
        result = await db.execute(query, {"chat_id": chat_id})
        row = result.fetchone()
        if row:
            row_dict = dict(zip(result.keys(), row))
        return row_dict


async def get_messages_by_chat_id(chat_id: uuid.UUID):
    query = text(
        """
        SELECT id, chat_id, role, content, created_at FROM message
        WHERE chat_id = :chat_id
        ORDER BY created_at ASC
    """
    )
    async with get_chat_db() as db:
        result = await db.execute(query, {"chat_id": str(chat_id)})
        rows = result.fetchall()
        return [dict(zip(result.keys(), row)) for row in rows]


async def get_message_by_id(message_id: uuid.UUID):
    row_dict = None
    query = text(
        """
        SELECT * FROM message
        WHERE id = :message_id
        LIMIT 1
    """
    )
    async with get_chat_db() as db:
        row_dict = None
        result = await db.execute(query, {"message_id": message_id})
        row = result.fetchall()
        if row:
            row_dict = dict(zip(result.keys(), row))
        return row_dict


async def delete_messages_after_timestamp(chat_id: str, timestamp: datetime) -> int:
    query = text(
        """
        DELETE FROM message
        WHERE chat_id = :chat_id AND created_at >= :timestamp
        RETURNING id
        """
    )
    params = {"chat_id": chat_id, "timestamp": timestamp}

    async with get_chat_db() as db:
        result = await db.execute(query, params)
        await db.commit()
        # Returns the number of rows deleted
        return result.rowcount
