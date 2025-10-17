"""
WebSocket-based implementation for Ada Chat with intermediate step streaming (continuous flow).

This module defines a WebSocket endpoint that receives chat payloads (similar
to the previous REST endpoint) and streams back events for intermediate steps
and a final answer. Unlike a one-shot flow, the connection remains open to
allow multiple "invoke" messages. The frontend is expected to close the
connection when done (e.g., when leaving the page).

References and Resources:
-------------------------
1. FastAPI WebSockets:
   https://fastapi.tiangolo.com/advanced/websockets/
2. Example Streaming Approaches with LLMs:
   - Official LangChain streaming docs: https://python.langchain.com/en/latest/modules/agents/agent_tutorial.html (search "Streaming")
   - OpenAI streaming docs: https://platform.openai.com/docs/guides/chatgpt/chatgpt-quickstart
3. Demonstration from the user's prior code snippet of “streaming from agent”:
   Showed how a conversation could yield intermediate steps/actions and then a final result.

"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional

from app.database.chat_queries import save_message, get_user_by_id
from app.agents.ada.build_ada import build_ada_chat_agent  # ADAPT: Ada agent logic
from app.utils.workflow_management import WorkflowManagement
from app.api_models.invoke_lisa import InvokeLisaResponse, LisaMessage
from app.config.env import ORGANIZATION_ID
from app.api_models.lisa_chat import (
    LisaChatReqeuest,
)  # If you have an Ada-specific request model, update here
from app.utils.model_to_message import model_to_message

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ada-chat-ws")
async def ada_chat_websocket(websocket: WebSocket):
    """
    WebSocket endpoint that streams conversation steps from Ada continuously,
    allowing the connection to remain persistent across multiple invocations.

    Usage Flow:
    -----------
    1) The client connects to /ada-chat-ws (WebSocket).
    2) The client sends JSON messages of various types. Supported:
       - "invoke": triggers a new Ada invocation with payload:
           {
             "type": "invoke",
             "payload": {
               "chatId": 1234,
               "messages": [
                 {"role": "user", "content": "Hello Ada!"},
                 ...
               ]
             }
           }
         The server processes those messages via the agent and streams responses:
            * "intermediate_step"
            * "final_response"
       - "close": instructs the server to break out of loop and close connection:
           {
             "type": "close"
           }
    3) The server sends back events:
       - intermediate_step:
          {
             "type": "intermediate_step",
             "content": "Partial chunk or status from the agent"
          }
       - final_response:
          {
             "type": "final_response",
             "content": "The final LLM response text",
             "role": "assistant",
             "workflow": [...]
          }
       - error:
          {
             "type": "error",
             "content": "Error details"
          }

    4) The connection remains open after a final_response. The client can send
       another "invoke" to continue. The client must send a "close" message or
       terminate the connection explicitly to end this session.

    Implementation Detail:
    ----------------------
    - If the client disconnects mid-stream, we catch the WebSocketDisconnect,
      mark the client as 'disconnected', but keep iterating over the agent's output
      so that we can still obtain and save the final response in the database.
    - If the chunk is a dict and has the key "output", we treat it as a final_response.
    - Otherwise, if the chunk is non-empty, we send it back as an "intermediate_step"
      (unless the client has disconnected).
    - If an empty chunk arises, we log it and ignore it.
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted at /ada-chat-ws")

    # Instantiate the Ada chat agent.
    workflow_manager = WorkflowManagement(user_id="", organization_id=ORGANIZATION_ID)
    ada_agent = await build_ada_chat_agent(workflow_manager)

    try:
        while True:
            # Continuously wait for incoming messages (invoke or close).
            try:
                message_text = await websocket.receive_text()
            except WebSocketDisconnect:
                logger.info("Client disconnected from /ada-chat-ws.")
                break  # No further messages to read from client

            if not message_text:
                # If empty or None, skip
                logger.warning("Received empty message, ignoring...")
                continue

            # Parse the incoming data
            try:
                data = json.loads(message_text)
            except json.JSONDecodeError:
                error_payload = {"type": "error", "content": "Invalid JSON payload."}
                await websocket.send_text(json.dumps(error_payload))
                continue

            msg_type = data.get("type")
            if msg_type == "close":
                logger.info("Received 'close' request from client. Closing loop.")
                break
            elif msg_type != "invoke":
                error_payload = {
                    "type": "error",
                    "content": "Invalid message type. Expected 'invoke' or 'close'.",
                }
                await websocket.send_text(json.dumps(error_payload))
                continue

            # Here msg_type == "invoke"
            payload = data.get("payload", {})
            chat_id = payload.get("chatId")
            ada_payload = payload.get("messages")
            try:
                logger.error(payload)
                user_id = payload.get("userId")
                user_dict = await get_user_by_id(user_id)
                logger.error(f"user info: {user_dict}")
            except Exception as error:
                logger.error(f"Could not get user: {str(error)}")
                user_dict = {"name": "unknown"}

            if not chat_id or not ada_payload:
                error_payload = {
                    "type": "error",
                    "content": "Both 'chatId' and 'messages' are required in payload.",
                }
                await websocket.send_text(json.dumps(error_payload))
                continue

            # Convert to standard Lisa/Ada messages.
            messages = [model_to_message(msg) for msg in ada_payload]
            if not messages:
                error_payload = {
                    "type": "error",
                    "content": "No valid messages found.",
                }
                await websocket.send_text(json.dumps(error_payload))
                continue

            input_msg = f"Name-{user_dict['name']}: {messages[-1]}"
            history_msgs = messages[:-1]

            client_disconnected = False

            # Stream from the Ada agent
            try:
                async for chunk in ada_agent.astream(
                    input=input_msg, chat_history=history_msgs
                ):
                    logger.debug(f"Chunk from agent: {chunk}")

                    if not chunk:
                        logger.warning("Received empty chunk from agent, ignoring.")
                        continue

                    # Check if the chunk is a dict AND has "output" (final response)
                    if isinstance(chunk, dict) and "output" in chunk:
                        final_answer = chunk["output"]
                        workflow_content = None
                        # Always save final message to DB, even if client disconnected
                        ada_message = LisaMessage(
                            role="assistant", content=final_answer
                        )
                        if (
                            workflow_manager.workflow_state
                            and len(workflow_manager.workflow_state) > 0
                        ):
                            workflow_content = [workflow_manager.workflow_state]

                        # else:
                        #     workflow_content = None
                        print(workflow_content)
                        await save_message(
                            chat_id=chat_id,
                            role=ada_message.role,
                            content={
                                "text": ada_message.content,
                                "workflow": workflow_content,
                            },
                        )

                        final_event = {
                            "type": "final_response",
                            "content": final_answer,
                            "role": "assistant",
                            "workflow": workflow_content,
                        }

                        # Attempt to send if still connected
                        if not client_disconnected:
                            try:
                                await websocket.send_text(json.dumps(final_event))
                            except WebSocketDisconnect:
                                logger.warning(
                                    "Client disconnected while sending final_response."
                                )
                                client_disconnected = True

                    else:
                        # It's an intermediate chunk
                        intermediate_event = {
                            "type": "intermediate_step",
                            "content": chunk,
                        }
                        # Attempt to send if still connected
                        if not client_disconnected:
                            try:
                                await websocket.send_text(
                                    json.dumps(intermediate_event)
                                )
                            except WebSocketDisconnect:
                                logger.warning(
                                    "Client disconnected during intermediate step."
                                )
                                client_disconnected = True

            except WebSocketDisconnect:
                logger.warning(
                    "WebSocketDisconnect caught inside streaming loop. Marking disconnected but continuing."
                )
                client_disconnected = True

    except Exception as e:
        logger.error(f"An unexpected error occurred in /ada-chat-ws: {e}")
    finally:
        logger.info("Closing WebSocket connection at /ada-chat-ws.")
        await websocket.close()
