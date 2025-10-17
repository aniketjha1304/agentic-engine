"""
Definition of lisa agent
"""

from textwrap import dedent
from agent_builder.builders.agent_builder import AgentBuilder
from agent_builder.builders.voice_agent_builder import VoiceAgentBuilder
from app.config.default import default_llm_dict
from app.agents.lisa.prompt.chat_prompt import get_chat_lisa_prompt
from app.agents.lisa.prompt.call_prompt import get_call_lisa_prompt
from app.utils.ai_brain import recaller_tool, encoder_tool
from app.agents.lisa.tools.get_datetime import create_get_datetime_tool
from app.agents.lisa.tools.get_workflow_details import create_get_workflow_details_tool
from app.agents.lisa.tools.get_workflows import create_get_workflows_tool
from app.agents.lisa.tools.end_twilio_call import create_end_twilio_call_tool
from app.agents.lisa.tools.execute_workflow import create_execute_workflow_tool
from app.agents.lisa.tools.get_csg_website_content import (
    create_get_csg_website_content_tool,
)
from app.config.env import (
    AZURE_GPT4O_REALTIME_PREVIEW_URL,
    AZURE_GPT4O_REALTIME_PREVIEW_KEY,
)
from pydantic import BaseModel, Field

from agent_builder.builders.tool_builder import ToolBuilder
from app.utils.logger import get_logger


async def build_lisa_chat_agent():
    lisa_prompt = await get_chat_lisa_prompt()
    agent_builder = AgentBuilder()
    agent_builder.set_goal(dedent(lisa_prompt))
    agent_builder.set_llm(default_llm_dict["azure_openai_gpt4o"])

    # Add the retrieval tool to the agent
    lisa_tools = get_lisa_tools()
    for tool in lisa_tools:
        agent_builder.add_tool(tool)
    # Build and return the agent
    lisa = agent_builder.build()
    return lisa


async def build_lisa_voice_agent(
    request_processor_object: object,
    audio_format: str = "pcm16",
    voice: str = "alloy",
    call_sid: str = None,
):
    ask_request_processor_tool = create_ask_request_processor_tool(
        request_processor_object
    )
    end_call_tool = create_end_twilio_call_tool(call_sid=call_sid)
    lisa_prompt = await get_call_lisa_prompt()
    builder = (
        VoiceAgentBuilder()
        .set_api_key(AZURE_GPT4O_REALTIME_PREVIEW_KEY)
        .set_model_url(AZURE_GPT4O_REALTIME_PREVIEW_URL)
        .set_goal(lisa_prompt)
        .set_voice(voice)  # Use 'alloy' voice for consistent audio output
        .set_input_audio_format(
            audio_format
        )  # Match Twilio's input audio format (g711_ulaw)
        .set_output_audio_format(
            audio_format
        )  # Match Twilio's output audio format (g711_ulaw)
        .set_tools([ask_request_processor_tool, end_call_tool])
        .set_turn_detection(
            # {
            #     "type": "server_vad",
            #     "threshold": 0.6,
            #     "prefix_padding_ms": 500,
            #     "silence_duration_ms": 1000,
            # }
            # NOTE: The semantic vad is not yet released in Azure
            {
                "type": "semantic_vad",
                "eagerness": "auto",
                # "create_response": true, // only in conversation mode
                # "interrupt_response": true, // only in conversation mode
            }
        )
    )

    voice_agent = builder.build()
    return voice_agent


def get_lisa_tools():
    lisa_tools = [
        # recaller_tool,
        # encoder_tool,
        # create_get_datetime_tool(),
        create_get_workflow_details_tool(),
        # create_get_workflows_tool(),
        create_execute_workflow_tool(),
        # create_get_csg_website_content_tool(),
    ]
    return lisa_tools


#### create the tool for lisa voice
class RequestProcessor(BaseModel):
    """
    Tool to communicate with request processor.
    """

    request: str = Field(
        description=("Detailed request to be processed by assistant with all context."),
    )


async def request_processor(request: str) -> str:
    """
    Process the request using lisa.
    """
    try:
        lisa_agent = await build_lisa_chat_agent()
        lisa_response = await lisa_agent.ainvoke(input=request, chat_history=[])
        return lisa_response["output"]
    except Exception as e:
        return f"Error while processing request ({str(e)})"


def create_ask_request_processor_tool(request_processor_object: object):
    """
    Build and return the tool for searching content on a website.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="ask-request-processor")
    tool_builder.set_function(request_processor_object.ainvoke)
    tool_builder.set_coroutine(request_processor_object.ainvoke)
    tool_builder.set_description(
        description=(
            """
        Use the Request Processor for all booking and apartment-related tasks, including:

        - Providing steps for booking an apartment  
        - Checking availability (dates, guest count)  
        - Verifying or creating customer records  
        - Managing bookings (reservations, payment links)  
        - Sending emails (confirmations, reminders)  
        - Handling general apartment queries  
        - Escalating to the manager via email when needed

        IMPORTANT:
        - Always include all required details (full name, email, dates) in each call. The processor does not retain context between requests.  
        - If a request is outside supported actions, inform the user and escalate to a manager.  
        - Respect privacy: if the user does not consent to data use, do not proceed with booking.
        """
        )
    )
    tool_builder.set_schema(schema=RequestProcessor)
    return tool_builder.build()
