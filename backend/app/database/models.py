from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()


class Chat(Base):
    __tablename__ = "chat"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    title = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)

    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "message"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chat.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(JSON, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    chat = relationship("Chat", back_populates="messages")
