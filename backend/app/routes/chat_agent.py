"""
Main Chat Agent endpoint - Handles chat messages with dynamic agent invocation
"""

from fastapi import APIRouter, HTTPException, Depends
from app.database.schemas import ChatMessageRequest, ChatMessageResponse, Message
from app.database.new_chat_queries import (
    get_chat_by_id,
    add_message_to_chat,
)
from app.services.agent_service import build_agent_runtime
from app.utils.api_key_required import api_key_required
from app.tools.list_workflows import (
    get_last_interactive_workflows,
    clear_interactive_workflows,
)
from app.tools.get_workflow_details import (
    get_last_interactive_workflow,
    clear_interactive_workflow,
)
from langchain_core.messages import HumanMessage, AIMessage
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def convert_messages_to_langchain(messages: list) -> list:
    """
    Convert database messages to LangChain message format

    Args:
        messages: List of Message objects from database

    Returns:
        List of LangChain messages
    """
    langchain_messages = []
    for msg in messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))
    return langchain_messages


@router.post(
    "/chat",
    dependencies=[Depends(api_key_required)],
    response_model=ChatMessageResponse,
    summary="Send message to agent",
    description="""
    Send a message to an agent in a chat session.
    
    This endpoint:
    1. Fetches the chat history
    2. Adds the user message to history
    3. Builds the agent at runtime with its configured prompts and workflows
    4. Invokes the agent with the message and history
    5. Saves the agent's response
    6. Returns the response
    """,
)
async def chat_with_agent(request: ChatMessageRequest):
    """
    Main chat endpoint that processes messages through configured agents

    Flow:
    1. Validate chat exists
    2. Fetch message history
    3. Add user message to chat
    4. Build agent runtime (with system prompt + workflow descriptions)
    5. Invoke agent with history
    6. Save assistant response
    7. Return response
    """
    try:
        # Fetch chat
        chat = await get_chat_by_id(request.chat_id)
        if not chat:
            raise HTTPException(
                status_code=404, detail=f"Chat '{request.chat_id}' not found"
            )

        logger.info(
            f"Processing message for chat {request.chat_id} with agent {request.agent_name}"
        )

        # Get existing message history
        message_history = chat.messages if chat.messages else []

        # Create user message
        user_message = Message(role="user", content=request.message)

        # Add user message to chat
        await add_message_to_chat(request.chat_id, user_message)

        # Convert messages to LangChain format
        langchain_history = convert_messages_to_langchain(message_history)

        # Build agent at runtime based on configuration
        agent = await build_agent_runtime(request.agent_name)

        # Invoke agent with message and history
        # Using the same pattern as build_lisa.py
        agent_response = await agent.ainvoke(
            input=request.message, chat_history=langchain_history
        )

        # Extract response text
        response_text = agent_response.get("output", "")

        # Check for interactive components
        additional_data = None

        # Check if list_workflows was used with interactive component
        workflows_data = get_last_interactive_workflows()
        if workflows_data:
            additional_data = {"workflows": workflows_data}
            clear_interactive_workflows()
            logger.info("Added workflows to interactive component")

        # Check if get_workflow_details was used with interactive component
        workflow_data = get_last_interactive_workflow()
        if workflow_data:
            additional_data = {"workflow": workflow_data}
            clear_interactive_workflow()
            logger.info("Added workflow details to interactive component")

        # Create assistant message with additional_data
        assistant_message = Message(
            role="assistant", content=response_text, additional_data=additional_data
        )

        # Save assistant message to chat
        await add_message_to_chat(request.chat_id, assistant_message)

        logger.info(f"Successfully processed message for chat {request.chat_id}")

        return ChatMessageResponse(
            message=response_text,
            chat_id=request.chat_id,
            additional_data=additional_data,
        )

    except HTTPException:
        raise
    except ValueError as e:
        # Agent not found or configuration error
        logger.error(f"Agent configuration error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process message. Please try again later.",
        )
