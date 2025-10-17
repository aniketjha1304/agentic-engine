from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.database.chat_queries import (
    save_message,
)
from app.agents.lisa.build_lisa import build_lisa_chat_agent
from app.api_models.invoke_lisa import InvokeLisaResponse, LisaMessage
from app.api_models.lisa_chat import LisaChatReqeuest
from app.utils.api_key_required import api_key_required
from app.utils.model_to_message import model_to_message
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/lisa-chat",
    dependencies=[Depends(api_key_required)],
    response_model=InvokeLisaResponse,
    summary="Process chat messages with Lisa AI",
    description="""Endpoint to process chat messages and generate a response using Lisa AI.
    Invoke Lisa with chat and explore her capabilities. This API returns lisa's response as well 
    as workflow object if any operation on workflow like get-details or creation/updation is done.
    This endpoint is coupled with the chat database and stores the response in chat database directly.
    """,
)
async def invoke_lisa(lisa_chat_request: LisaChatReqeuest):
    """
    Endpoint to process chat messages and generate a response.

    Returns
    -------
    dict
        Response from lisa_graph.
    """
    try:

        logger.info(f"Received request")

        # Extract required fields with error checking
        lisa_payload = lisa_chat_request.messages
        chat_id = lisa_chat_request.chatId
        # Validate the lisa_payload
        if not isinstance(lisa_payload, list) or not lisa_payload:
            logger.error("Invalid 'request' field: must be a non-empty list")
            raise HTTPException(
                status_code=400,
                detail="Invalid 'request' field: must be a non-empty list",
            )
        logger.info(f"Processing chat with ID: {chat_id}")

        messages = [model_to_message(msg.model_dump()) for msg in lisa_payload]
        lisa_agent = await build_lisa_chat_agent()
        lisa_response = await lisa_agent.ainvoke(
            input=messages[-1], chat_history=messages[:-1]
        )
        lisa_message = LisaMessage(role="assistant", content=lisa_response["output"])

        await save_message(
            chat_id=chat_id,
            role=lisa_message.role,
            content={
                "text": lisa_message.content,
                "workflow": lisa_response.get("workflow"),
            },
        )

        # Format and return Lisa's response.
        formatted_response = InvokeLisaResponse(
            message=[lisa_message],
            workflow=lisa_response.get("workflow"),
        )

        return formatted_response

    except Exception as e:
        logger.error(f"Unexpected error occurred while lisa chat: {str(e)}")
        role = "assistant"
        content = (
            "I am facing an issue at the moment, could you please try again later?"
        )
        fallback_response = InvokeLisaResponse(
            message=[
                LisaMessage(
                    role=role,
                    content=content,
                )
            ]
        )
        await save_message(chat_id=chat_id, role=role, content=content)
        return JSONResponse(content=fallback_response.model_dump(), status_code=500)
