from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.utils.api_key_required import api_key_required
from app.agents.lisa.build_lisa import build_lisa_chat_agent
from app.utils.model_to_message import model_to_message
from app.api_models.invoke_lisa import (
    InvokeLisaRequest,
    InvokeLisaResponse,
    LisaMessage,
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/invoke-lisa",
    dependencies=[Depends(api_key_required)],
    response_model=InvokeLisaResponse,
    summary="Process chat messages with Lisa AI",
    description="""Endpoint to process chat messages and generate a response using Lisa AI.
    Invoke Lisa with chat and explore her capabilities. This API returns lisa's response as well 
    as workflow object if any operation on workflow like get-details or creation/updation is done.
    """,
)
async def invoke_lisa(invoke_lisa_request: InvokeLisaRequest):
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
        lisa_payload = invoke_lisa_request.request
        messages = [model_to_message(msg.model_dump()) for msg in lisa_payload]
        lisa_agent = await build_lisa_chat_agent()
        lisa_response = await lisa_agent.ainvoke(
            input=messages[-1], chat_history=messages[:-1]
        )
        lisa_message = LisaMessage(role="assistant", content=lisa_response["output"])
        # Prepare and return the response
        response = InvokeLisaResponse(
            message=[lisa_message],
            workflow=lisa_response.get("workflow"),
        )
        return response

    except Exception as e:
        logger.exception("Unexpected error occurred")
        # Return a fallback response in case of unexpected errors
        fallback_response = InvokeLisaResponse(
            message=[
                LisaMessage(
                    role="assistant",
                    content="I am facing an issue at the moment, could you please try again later?",
                )
            ]
        )
        return JSONResponse(content=fallback_response.model_dump(), status_code=200)
