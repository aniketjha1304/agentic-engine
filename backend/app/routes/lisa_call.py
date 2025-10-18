# """
# Module for setting up the WebSocket endpoint for Lisa, the material planning assistant.

# This module defines the `/lisa-call` WebSocket endpoint using FastAPI, which allows
# clients to interact with the `VoiceAgent` named Lisa AI. The agent uses OpenAI's Realtime
# API to process voice input and produce voice responses, orchestrating workflows, and
# leveraging tools to fulfill user requests.

# Payload and response structures are based on the OpenAI Realtime API specifications.
# """

# import asyncio
# import logging
# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from app.agents.lisa.build_lisa import build_lisa_voice_agent
# from app.utils.websocket_stream import websocket_stream


# logger = logging.getLogger(__name__)
# router = APIRouter()


# @router.websocket("/lisa-call")
# async def lisa_call_endpoint(websocket: WebSocket) -> None:
#     """
#     WebSocket endpoint for interacting with Lisa, the material planning assistant.

#     This endpoint accepts a WebSocket connection and allows clients to stream audio
#     input to Lisa and receive audio responses. It builds the `VoiceAgent` with the
#     appropriate tools and manages the communication with the OpenAI Realtime API.

#     Parameters
#     ----------
#     websocket : WebSocket
#         The WebSocket connection from the client.

#     Expected Payload
#     ----------------
#     The client should send events formatted as per the OpenAI Realtime API.
#     For example:
#     - To append audio data:

#       ```json
#       {
#           "type": "input_audio_buffer.append",
#           "audio": "Base64EncodedAudioData"
#       }
#       ```

#     - To commit the audio buffer (if not using server-side VAD):

#       ```json
#       {
#           "type": "input_audio_buffer.commit"
#       }
#       ```

#     Response Structure
#     ------------------
#     The server sends events back to the client, including:

#     - **Audio responses**:

#       ```json
#       {
#           "type": "response.audio.delta",
#           "delta": "Base64EncodedAudioDelta"
#       }
#       ```

#     - **Notifications of speech start**:

#       ```json
#       {
#           "type": "input_audio_buffer.speech_started",
#           "audio_start_ms": 1000,
#           "item_id": "msg_003"
#       }
#       ```

#     - **Error messages**:

#       ```json
#       {
#           "type": "error",
#           "error": {
#               "message": "Error message",
#               "code": "error_code"
#           }
#       }
#       ```
#     """
#     await websocket.accept()
#     # await asyncio.sleep(1)  # Allow time for connection stabilization
#     try:
#         # Receive data from the browser via websocket
#         initial_message = {
#             "type": "response.create",
#             "response": {
#                 "modalities": ["text", "audio"],
#                 "voice": "alloy",
#                 "output_audio_format": "pcm16",
#             },
#         }

#         # Receive data from the browser via websocket, including the initial message
#         browser_receive_stream = websocket_stream(
#             websocket, initial_message=initial_message
#         )

#         voice_agent = await build_lisa_voice_agent(audio_format="pcm16")

#         # Invoke the agent with the combined stream
#         await voice_agent.ainvoke(browser_receive_stream, websocket.send_text)

#     except WebSocketDisconnect:
#         logger.info("Client disconnected")
#     except Exception as e:
#         logger.error(f"An error occurred: {e}")
#         await websocket.close(code=1001, reason="Internal server error")
