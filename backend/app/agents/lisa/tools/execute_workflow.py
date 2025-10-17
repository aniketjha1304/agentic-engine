import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from agent_builder.builders.tool_builder import ToolBuilder
from app.utils.execute_http_trigger_workflow import execute_http_trigger_workflow
from app.utils.logger import get_logger

# Get a logger for this module
logger = get_logger(name=__name__)


class ExecuteWorkflow(BaseModel):
    """
    Tool to execute a skill based on the given title and input parameters.
    """

    skill_title: str = Field(
        ..., description="The title of the skill to be executed."
    )
    input_parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "A dictionary of input parameters matching the skill's input "
            "signature. Check the skill details for required parameters."
        ),
    )
    # wait_for_response: Optional[bool] = Field(
    #     default=False,
    #     description="""
    #     Determines whether to wait for the workflow execution to complete and return the response.
    #     If set to `True`, the function will wait for execution to finish before proceeding.
    #     Since some workflows may take time to complete, enable this option only if it is explicitly
    #     stated in the workflow description that waiting is necessary or the execution is expected to be quick.
    #     By default, this is set to `False`.
    #     """,
    # )


# NOTE: Set the wait_for_response as True in this case for bookings
async def execute_workflow(
    skill_title: str,
    input_parameters: Optional[Dict[str, Any]] = None,
    wait_for_response: bool = True,
) -> str:
    """
    Execute a workflow based on the given title and input parameters.

    Args:
        skill_title (str): The title of the workflow to be executed.
        input_parameters (Optional[Dict[str, Any]]): Input parameters matching
            the workflow's input signature.

    Returns:
        Union[str, Command]: A response message or a Command to go to
            "gating_assistant".
    """
    try:
        data = await execute_http_trigger_workflow(
            workflow_title=skill_title,
            input_parameters=input_parameters,
            wait_for_response=wait_for_response,
        )
        logger.info("Data from execution of skill")
        logger.info(data)
        response_message = data["message"]
        return response_message

    except Exception as e:
        # Handle exceptions and return an error message
        response_message = f"Error executing skill: {str(e)}"
        return response_message


def create_execute_workflow_tool():
    """
    Build and return the tool for executing workflows.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="execute-skill")
    tool_builder.set_function(execute_workflow)
    tool_builder.set_coroutine(execute_workflow)
    tool_builder.set_description(
        description=(
            """Use this tool to execute your skills based on the specified title and the required input parameters, if applicable.  
            If the skill does not require any input parameters, execute without them.  

            This is most efficient way to execute your skills and complete the task.

            
            """
        )
    )
    tool_builder.set_schema(schema=ExecuteWorkflow)
    return tool_builder.build()
