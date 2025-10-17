"""
Get workflow details with code for given workflow title.
"""

import os
from typing import Optional, List
from typing_extensions import Annotated, Literal

import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.runnables.config import RunnableConfig
from agent_builder.builders.tool_builder import ToolBuilder
from app.utils.get_existing_workflow_code import get_existing_workflow_code
from app.database.ai_persona_hub_queries import get_workflow_by_title
from app.utils.get_workflow_trigger_data import get_workflow_trigger_data
from app.utils.get_workflow_diagram import get_workflow_diagram
from app.graph.graph_state import Workflow


class GetWorkflowDetails(BaseModel):

    workflow_title: str = Field(
        description=("The title of the workflow for which details are to be fetch."),
    )
    # NOTE: Need to add this in args so that ToolNode understands and pass state.
    state: Annotated[dict, InjectedState] = Field(
        description=("State of the graph"),
    )


async def get_workflow_details(
    config: RunnableConfig,
    state: Annotated[dict, InjectedState],
    workflow_title: str,
) -> Command[Literal["gating_assistant"]]:
    """
    Fetch workflows based on the given title or return all workflows.
    Optionally include the associated code in the details.

    Args:
        workflow_title str: The title of the workflow to fetch.

    Returns:
        str: A response message containing workflow details and optionally the code.
    """
    workflow_data = None
    response_message = ""
    workflow_state_data = None

    try:
        workflow_data = await get_workflow_by_title(title=workflow_title)
        # Check if any workflows were found
        if not workflow_data:
            response_message = (
                "No workflows found matching the criteria."
                if workflow_title is None
                else f"No workflow found with title '{workflow_title}'."
            )
            return Command(
                update={"messages": [ToolMessage(content=response_message)]},
                goto="gating_assistant",
            )
        trigger_data = await get_workflow_trigger_data(
            workflow_id=workflow_data["id"], trigger_type=workflow_data["type"]
        )

        file_content = await get_existing_workflow_code(title=workflow_title)

        workflow_state_data = Workflow(
            id=workflow_data.get("id", ""),
            title=workflow_data.get("title", ""),
            description=workflow_data.get("description", ""),
            content=file_content,
            diagram=get_workflow_diagram(workflow_code=file_content),
            metadata=workflow_data.get("metadata", {}),
            status=workflow_data.get("status", ""),
        )

        # Create a response message with workflow details and code
        response_message = (
            f"Workflow Details:\n"
            f"ID: {workflow_data.get('id', 'N/A')}\n"
            f"Title: {workflow_data.get('title', 'N/A')}\n"
            f"Description: {workflow_data.get('description', 'N/A')}\n\n"
            f"Additional Data: {trigger_data}\n"
            f"Workflow Code:\n"
            f"{file_content}"
        )

    except Exception as e:
        # Handle exceptions and return an error message
        response_message = f"Error fetching workflow details: {str(e)}"

    # Update state and return command
    tool_call = state["messages"][-1].tool_calls[0]
    tool_message = ToolMessage(content=response_message, tool_call_id=tool_call["id"])
    update = {
        "messages": [tool_message],
        "workflow": [workflow_state_data] if workflow_state_data is not None else [],
    }

    return Command(update=update, goto="gating_assistant")


def create_get_workflow_details_tool():
    """
    Build and return the tool for fetching workflow and their associated code.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="GetWorkflowDetails")
    tool_builder.set_function(get_workflow_details)
    tool_builder.set_coroutine(get_workflow_details)
    tool_builder.set_description(
        description=(
            """
            Use this tool to retrieve details of a workflow based on the provided title.
            It fetches the workflow's details, including its code. The workflow code
            is displayed to the user on the UI and made available to you as well for interpretation.
            """
        )
    )
    tool_builder.set_schema(schema=GetWorkflowDetails)
    return tool_builder.build()
