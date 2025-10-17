import os
from typing import Optional, List
from typing_extensions import Annotated, Literal

import pandas as pd
from pydantic import BaseModel, Field

from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.runnables.config import RunnableConfig

from app.utils.dataframe_to_markdown import dataframe_to_markdown
from app.database.ai_persona_hub_queries import get_workflows_list
from agent_builder.builders.tool_builder import ToolBuilder


class GetWorkflows(BaseModel):
    """Get workflows list"""


# NOTE: This is a ToolNode and hence command is not applicable.
async def get_workflows(
    # config: RunnableConfig,
    # state: Annotated[dict, InjectedState],
):
    """
    Fetch workflows based on the given title or return all workflows.
    Include the details in the response message, formatted as a markdown table.

    Args:
        config (RunnableConfig): The configuration for the runnable.
        state (dict): The injected state dictionary.
        workflow_title (Optional[str]): The title of the workflow to fetch.
            If None, all workflows are fetched.

    Returns:
        Command: Contains the response message and direction for the workflow.
    """
    # TODO: Implement asynchronous postgres
    try:
        # Create a Postgres connector to fetch workflows
        result = await get_workflows_list()

        # Check if any workflows were found
        if not result:
            response_message = "No workflows found matching the criteria."
            return response_message

        # Convert result to DataFrame
        df = pd.DataFrame(result)

        # Format DataFrame as markdown table
        markdown_table = dataframe_to_markdown(df)

        response_message = f"Workflows\n{markdown_table}"
        return response_message
    except Exception as e:
        # Handle exceptions and return an error message
        response_message = f"Error fetching workflows: {str(e)}"
        return response_message


def create_get_workflows_tool():
    """
    Build and return the tool for fetching workflows.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="GetWorkflows")
    tool_builder.set_function(get_workflows)
    tool_builder.set_coroutine(get_workflows)
    tool_builder.set_description(
        description=("Use this tool to fetch list of workflows")
    )
    tool_builder.set_schema(schema=GetWorkflows)
    return tool_builder.build()
