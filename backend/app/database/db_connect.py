from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config.env import AI_PERSONA_HUB_DB_URL, CHAT_DB_URL
from contextlib import asynccontextmanager  # Import asynccontextmanager

# Create engines for both databases
if CHAT_DB_URL.startswith("postgresql://"):
    CHAT_DB_URL = CHAT_DB_URL.replace("postgresql://", "postgresql+asyncpg://")

if AI_PERSONA_HUB_DB_URL.startswith("postgresql://"):
    AI_PERSONA_HUB_DB_URL = AI_PERSONA_HUB_DB_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    )

# Create async engines
chat_db_engine = create_async_engine(CHAT_DB_URL, echo=True)
ai_persona_hub_db_engine = create_async_engine(AI_PERSONA_HUB_DB_URL, echo=True)

# Session factory for async sessions
chat_db_session = sessionmaker(
    chat_db_engine, class_=AsyncSession, autocommit=False, autoflush=False
)

ai_persona_hub_db_session = sessionmaker(
    ai_persona_hub_db_engine, class_=AsyncSession, autocommit=False, autoflush=False
)

Base = declarative_base()


# Async context manager to get the session
@asynccontextmanager
async def get_ai_persona_hub_db():
    """Dependency to provide a database session for AI_PERSONA_HUB_DB."""
    async with ai_persona_hub_db_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_chat_db():
    """Dependency to provide a database session for CHAT_DB."""
    async with chat_db_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
