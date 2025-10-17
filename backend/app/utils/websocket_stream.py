from typing import AsyncIterator, Optional
from fastapi.websockets import WebSocket
import json


async def websocket_stream(
    websocket: WebSocket, initial_message: Optional[dict] = None
) -> AsyncIterator[str]:
    # Yield the initial message if provided
    if initial_message is not None:
        # Convert the initial message to JSON string
        yield json.dumps(initial_message)
    # Continue receiving messages from the WebSocket
    while True:
        data = await websocket.receive_text()
        yield data
