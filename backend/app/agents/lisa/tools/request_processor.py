# from pydantic import BaseModel, Field

# from agent_builder.builders.tool_builder import ToolBuilder
# from app.utils.logger import get_logger
# from app.agents.lisa.build_lisa import build_lisa_chat_agent

# # Get a logger for this module
# logger = get_logger(name=__name__)


# class RequestProcessor(BaseModel):
#     """
#     Tool to communicate with request processor.
#     """

#     request: str = Field(
#         description=("Detailed request to be processed by assistant with all context."),
#     )


# async def request_processor(request: str) -> str:
#     """
#     Process the request using lisa.
#     """
#     try:
#         lisa_agent = await build_lisa_chat_agent()
#         lisa_response = await lisa_agent.ainvoke(input=request, chat_history=[])
#         return lisa_response["output"]
#     except Exception as e:
#         return f"Error while processing request ({str(e)})"


# def create_ask_request_processor_tool():
#     """
#     Build and return the tool for searching content on a website.
#     """
#     tool_builder = ToolBuilder()
#     tool_builder.set_name(name="ask-request-processor")
#     tool_builder.set_function(request_processor)
#     tool_builder.set_coroutine(request_processor)
#     tool_builder.set_description(
#         description=(
#             """Use this tool to handle any booking or apartment-related functionality. 
#             This single consolidated tool could be used for:

#             - Checking apartment availability.
#             - Verifying or creating customer records.
#             - Managing bookings (creating booking and processing payments).
#             - Sending automated emails (confirmation, payment links, etc.).
#             - Handling additional actions (like scheduling cleaning or special services).

#             The “Request Processor” is how you can take actions or process user requests.
#             Anything the processor cannot do, you also cannot do. The processor does not 
#             remember context from previous conversations, so each request must be detailed.

#         """
#         )
#     )
#     tool_builder.set_schema(schema=RequestProcessor)
#     return tool_builder.build()
