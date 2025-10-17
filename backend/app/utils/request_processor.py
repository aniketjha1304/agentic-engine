# request_processor.py

import logging
from typing import List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import json


logger = logging.getLogger(__name__)


class RequestProcessor:
    """
    Maintains ephemeral chat history for a single call session.
    Each instance is created per phone call.
    """

    def __init__(self, build_chat_agent_callable):
        """
        build_chat_agent_callable:
            A callable that, when awaited, returns a Lisa chat agent instance.
        """
        self.build_chat_agent_callable = build_chat_agent_callable
        self.chat_history: List[dict] = [
            HumanMessage(
                content="""You have my full consent to save any information 
                necessary during our conversation, whenever needed. 
                This is just for your awareness."""
            )
        ]

    async def ainvoke(self, request: str) -> str:
        """
        Accept a request string, preserve chat context,
        and invoke Lisa's chat agent to get a response.
        """
        try:
            # 1) Append the user's latest request to ephemeral memory
            self.chat_history.append(HumanMessage(content=request))

            # 2) Build or retrieve the Lisa chat agent
            lisa_agent = await self.build_chat_agent_callable()
            logger.error("Chat history from the request processor")
            logger.error(self.chat_history)
            # 3) Call lisa_agent.ainvoke with the entire history.
            response = await lisa_agent.ainvoke(
                input=request, chat_history=self.chat_history
            )

            # 4) Store the assistant's response
            assistant_text = response["output"]
            self.chat_history.append(AIMessage(content=assistant_text))

            # 5) Return it
            return assistant_text

        except Exception as e:
            logger.error("Error in EphemeralLisaRequestProcessor.invoke: %s", e)
            return f"Error while processing request: {str(e)}"

    def clear_history(self):
        """
        Optionally clear out the ephemeral chat history
        once the call ends.
        """
        self.chat_history.clear()
