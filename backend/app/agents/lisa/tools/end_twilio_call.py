from pydantic import BaseModel
from agent_builder.builders.tool_builder import ToolBuilder
from app.utils.logger import get_logger
from twilio.rest import Client
from app.config.env import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from agent_builder.utils.call_end_exception import CallEndException

# Logger
logger = get_logger(name=__name__)


class EndCallSchema(BaseModel):
    """
    End the call.
    """


class EndCallHandler:
    """
    Class to handle Twilio call termination.
    The call_sid is fixed per call and injected during tool creation.
    """

    def __init__(self, call_sid: str):
        self.call_sid = call_sid
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    async def end_call(self) -> str:
        """
        Ends the Twilio call gracefully.
        """
        # try:
        # self.client.calls(self.call_sid).update(status="completed")
        # self.client.calls(self.call_sid).update(
        #     twiml="<Response><Hangup/></Response>"
        # )
        # logger.info(f"Successfully ended Twilio call with SID: {self.call_sid}")
        # return "The call has been successfully ended."
        # except Exception as e:
        #     logger.error(f"Error ending call SID {self.call_sid}: {e}")
        #     return "There was an issue while ending the call."
        logger.info(f"Proceedingto end the call: {self.call_sid}")

        # Raise an exception to halt further execution
        raise CallEndException("End the call exception.")


def create_end_twilio_call_tool(call_sid: str):
    """
    Builds the 'end-twilio-call' tool with a fixed call_sid.

    The agent should use this tool only after confirming the user's task is completed
    and clearly stating the call will be ended.
    """
    end_call_handler = EndCallHandler(call_sid)

    tool_builder = ToolBuilder(enable_exception_handling=False)
    tool_builder.set_name(name="end-call")
    tool_builder.set_function(end_call_handler.end_call)
    tool_builder.set_coroutine(end_call_handler.end_call)
    tool_builder.set_description(
        description=(
            """Use this tool to gracefully end call after you’ve confirmed the user’s needs 
            are fulfilled. **Never use this before asking the user if they need anything else or confirming**.

            Before triggering the tool, say something like:
            _“If there’s nothing else, I’ll go ahead and end the call now. Thank you for your time!”_

            Only use this tool once the user explicitly or implicitly agrees to end the call.
            """
        )
    )
    tool_builder.set_schema(schema=EndCallSchema)
    return tool_builder.build()
