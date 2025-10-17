import os
from dotenv import load_dotenv
from typing_extensions import Literal
from langgraph.types import Command
from langchain_core.messages import SystemMessage
from app.graph.graph_state import LisaState
from app.config.default import default_llm_dict

from pydantic import BaseModel, Field
from recall_space_agents.toolkits.ms_email.ms_email import MSEmailToolKit
from recall_space_agents.toolkits.ms_site.ms_site import MSSiteToolKit
from recall_space_agents.toolkits.ms_site_workbook.ms_site_workbook import (
    MSSiteWorkbookToolKit,
)
from recall_space_agents.toolkits.ms_todo.ms_todo import MSTodoToolKit
from azure.identity import UsernamePasswordCredential
from app.utils.determine_next_action import (
    determine_next_action,
    NextActionType,
)
from app.graph.default import tool_name_to_assistant_name
from app.utils.route_conversation import transfer_to_supervisor
from app.config.env import LISA_PASSWORD, LISA_USER_NAME, CLIENT_ID, TENANT_ID

load_dotenv()


class DelegateToTaskExecutor(BaseModel):
    """
    Use this tool to delegate to task executor. The task executor assistant
    is an expert in executing ad hoc tasks of a material planner using the
    tools. Use this tool when the user wants you to create, update, or delete
    their To-Do list, email someone, check data from SharePoint, manipulate
    Excel files, etc.
    """

    message: str = Field(..., description="Message for workflow assistant.")


async def task_executor_assistant(state: LisaState) -> Command[
    Literal[
        "task_executor_tools",
        "gating_assistant",
    ]
]:
    system_prompt = """
    You are a task executor assistant specialized as a material planner. Your 
    primary goal is to assist users by executing tasks using the available 
    tools. Interpret the user's instructions and use the provided tools to 
    fulfill their requests in a simple and straightforward manner.
    """
    sys_msg = SystemMessage(content=system_prompt)

    # Initialize the credentials for MS toolkits
    credentials = UsernamePasswordCredential(
        client_id=CLIENT_ID,
        username=LISA_USER_NAME,
        password=LISA_PASSWORD,
        tenant_id=TENANT_ID,
        authority="https://login.microsoftonline.com/",
    )

    # Instantiate toolkits and gather tools
    ms_todo_tool_kit = MSTodoToolKit(credentials=credentials)
    tools_todo = ms_todo_tool_kit.get_tools()

    ms_email_tool_kit = MSEmailToolKit(credentials=credentials)
    tools_email = ms_email_tool_kit.get_tools()
    tools_email.pop(1)
    ms_sites_tool_kit = MSSiteToolKit(credentials=credentials)
    tools_sites = ms_sites_tool_kit.get_tools()

    ms_sites_workbook_tool_kit = MSSiteWorkbookToolKit(credentials=credentials)
    tools_sites_workbook = ms_sites_workbook_tool_kit.get_tools()

    llm = default_llm_dict["azure_openai_gpt4o"]

    # Combine all tools and bind them to the LLM
    task_executor_tools = tools_todo + tools_email + tools_sites + tools_sites_workbook
    llm_with_tools = llm.bind_tools(task_executor_tools, parallel_tool_calls=False)

    # Invoke the LLM with the system message and conversation history
    print(state["task_executor_messages"])
    response = await llm_with_tools.ainvoke([sys_msg] + state["task_executor_messages"])

    action_type, next_action = determine_next_action(
        response, tool_name_to_assistant_name
    )

    if action_type == NextActionType.END:
        next_action = "gating_assistant"
        update = transfer_to_supervisor(
            state=state, response=response, agent_name="task_executor_assistant"
        )
    else:
        next_action = "task_executor_tools"
        update = {"task_executor_messages": [response]}

    return Command(
        update=update,
        goto=next_action,
    )
