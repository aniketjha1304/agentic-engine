import os
from typing import Optional, Dict, Any, Union
import json
import aiohttp
from pydantic import BaseModel, Field
from typing_extensions import Literal

from langgraph.types import Command

from agent_builder.builders.tool_builder import ToolBuilder
from app.utils.execute_http_trigger_workflow import execute_http_trigger_workflow
from app.utils.logger import get_logger

# Get a logger for this module
logger = get_logger(name=__name__)


class ExecuteWorkflow(BaseModel):
    """
    Tool to execute a workflow based on the given title and input parameters.
    """

    workflow_title: str = Field(
        ..., description="The title of the workflow to be executed."
    )
    input_parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "A dictionary of input parameters matching the workflow's input "
            "signature. Check the workflow details for required parameters."
        ),
    )


async def execute_workflow(
    workflow_title: str,
    input_parameters: Optional[Dict[str, Any]] = None,
) -> Union[str, Command[Literal["gating_assistant"]]]:
    """
    Execute a workflow based on the given title and input parameters.

    Args:
        config (RunnableConfig): The configuration for the current execution.
        state (dict): The current state of the workflow.
        workflow_title (str): The title of the workflow to be executed.
        input_parameters (Optional[Dict[str, Any]]): Input parameters matching
            the workflow's input signature.

    Returns:
        Union[str, Command]: A response message or a Command to go to
            "gating_assistant".
    """
    try:
        data = await execute_http_trigger_workflow(
            workflow_title=workflow_title, input_parameters=input_parameters
        )
        logger.info("Data from execution of worklfow")
        logger.info(data)
        response_message = data["message"]
        return response_message

    except Exception as e:
        # Handle exceptions and return an error message
        response_message = f"Error executing workflow: {str(e)}"
        return response_message


def create_execute_workflow_tool():
    """
    Build and return the tool for executing workflows.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="ExecuteWorkflow")
    tool_builder.set_function(execute_workflow)
    tool_builder.set_coroutine(execute_workflow)
    tool_builder.set_description(
        description=(
            """Executes a workflow based on the specified title and, if applicable,
             the provided input parameters. These parameters may be retrieved from the workflow details.

            Before execution, it is recommended to review the workflow details to 
            confirm whether input parameters are required.
            
            """
        )
    )
    tool_builder.set_schema(schema=ExecuteWorkflow)
    return tool_builder.build()
