"""
Module for setting up the WebSocket endpoint for Lisa, the material planning assistant.

This module defines the `/incoming-lisa-call` and `/media-stream` endpoints using FastAPI,
which allow Twilio Media Streams to send and receive audio data.
The agent uses OpenAI's Realtime API to process voice input and produce voice responses.

Payload and response structures are adjusted to comply with both Twilio's and OpenAI's
expected formats.
"""

import json
import asyncio
import logging
from typing import AsyncIterator, List

from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import Connect, VoiceResponse

from app.agents.lisa.build_lisa import build_lisa_voice_agent, build_lisa_chat_agent
from app.utils.request_processor import RequestProcessor
from agent_builder.utils.call_end_exception import CallEndException

logger = logging.getLogger(__name__)
router = APIRouter()


@router.api_route("/incoming-lisa-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """
    Handle incoming calls from Twilio and provide TwiML instructions to connect to the media stream.

    By default, Twilio hits this endpoint with a POST request when a call is initiated,
    and we respond with TwiML instructing Twilio to connect via the /media-stream WebSocket.
    Parameters
    ----------
    request : Request
        The incoming HTTP request from Twilio.

    Returns
    -------
    HTMLResponse
        An XML response containing TwiML instructions to start the media stream.
    """
    response = VoiceResponse()
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f"wss://{host}/media-stream")
    response.append(connect)

    return HTMLResponse(content=str(response), media_type="application/xml")


@router.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """
    WebSocket endpoint to handle audio data streaming between Twilio and OpenAI Realtime API.
    """
    await websocket.accept()
    stream_sid = None
    call_sid = None

    try:
        # Step 1: Wait for "start" event with the callSid
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            event = data.get("event")

            if event == "start":
                stream_sid = data["start"]["streamSid"]
                call_sid = data["start"]["callSid"]
                logger.info(
                    f"Stream started: streamSid={stream_sid}, callSid={call_sid}"
                )
                break

        # Step 2: Build the voice agent with the call_sid
        request_processor = RequestProcessor(
            build_chat_agent_callable=build_lisa_chat_agent
        )
        voice_agent = await build_lisa_voice_agent(
            audio_format="g711_ulaw",
            request_processor_object=request_processor,
            call_sid=call_sid,
        )

        # Step 3: Prepare the incoming audio (input_audio_stream)
        async def input_audio_stream() -> AsyncIterator[str]:
            # Send an initial message to the Realtime service
            initial_message = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "voice": "alloy",
                    "output_audio_format": "g711_ulaw",
                },
            }
            yield json.dumps(initial_message)

            # Then continually yield messages from Twilio
            async for message in websocket.iter_text():
                data = json.loads(message)
                event = data.get("event")

                if event == "media":
                    yield json.dumps(
                        {
                            "type": "input_audio_buffer.append",
                            "audio": data["media"]["payload"],
                        }
                    )
                elif event == "stop":
                    logger.info("Stream stopped by Twilio.")
                    break

        # Step 3b: This callback handles audio delta events or buffer clears
        async def handle_output_event(event_str: str):
            event = json.loads(event_str)
            event_type = event.get("type")

            # Audio to be played back to the user
            if event_type == "response.audio.delta" and "delta" in event:
                if stream_sid is not None:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {"payload": event["delta"]},
                            }
                        )
                    )

            # If the user started speaking again, clear Twilio's input buffer
            elif event_type == "input_audio_buffer.speech_started":
                if stream_sid:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "streamSid": stream_sid,
                                "event": "clear",
                            }
                        )
                    )
                    logger.info("Cleared Twilio input buffer on speech_start.")
            elif event_type == "call.end":
                logger.error(f"Lisa wants to disconnect the call.")
                raise CallEndException

        # Step 4: Run the agent
        await voice_agent.ainvoke(input_audio_stream(), handle_output_event)

    except CallEndException as e:
        # When the agent triggers a call-end, we close the websocket
        logger.error(f"CallEndException caught: {e}")
        await asyncio.sleep(3)
        await websocket.close(code=1001, reason="Call ended by agent.")
    except WebSocketDisconnect:
        logger.info("Caller disconnected.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.close(code=1001, reason="Internal server error")
