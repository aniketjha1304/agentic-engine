"""
Execute Workflow Tool - Executes workflows with input validation
"""

from pydantic import BaseModel, Field
from typing import Dict, Any
from agent_builder.builders.tool_builder import ToolBuilder
from app.services.workflow_execution_service import (
    execute_workflow as execute_workflow_service,
)
from app.utils.logger import get_logger
import json

logger = get_logger(__name__)


class ExecuteWorkflowInput(BaseModel):
    """Input schema for execute workflow tool"""

    workflow_name: str = Field(description="The name of the workflow to execute")
    input_data: str = Field(
        description="JSON string containing the input data for the workflow"
    )


async def execute_workflow_tool(workflow_name: str, input_data: str) -> str:
    """
    Execute a workflow with the provided input data

    Args:
        workflow_name: Name of the workflow to execute
        input_data: JSON string with input data

    Returns:
        String containing execution result
    """
    try:
        # Parse input data from JSON string
        try:
            parsed_input = json.loads(input_data)
        except json.JSONDecodeError as e:
            return f"Invalid JSON input: {str(e)}"

        # Execute workflow
        result = await execute_workflow_service(workflow_name, parsed_input)

        return f"Workflow '{workflow_name}' executed successfully. Result: {json.dumps(result, indent=2)}"

    except ValueError as e:
        logger.error(f"Validation error executing workflow: {str(e)}")
        return f"Validation error: {str(e)}"
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        return f"Error executing workflow: {str(e)}"


def create_execute_workflow_tool():
    """
    Build and return the execute workflow tool
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="execute_workflow")
    tool_builder.set_function(execute_workflow_tool)
    tool_builder.set_coroutine(execute_workflow_tool)
    tool_builder.set_description(
        description=(
            """Execute a workflow with the provided input data.
            This tool validates the input against the workflow's JSON schema and executes it.
            Provide the workflow name and input data as a JSON string.
            
            Example usage:
            - workflow_name: "send_email"
            - input_data: '{"to": "user@example.com", "subject": "Hello", "body": "Test message"}'
            """
        )
    )
    tool_builder.set_schema(schema=ExecuteWorkflowInput)
    return tool_builder.build()
