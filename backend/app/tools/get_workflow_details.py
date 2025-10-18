"""
Get Workflow Details Tool - Returns workflow code and input parameters
"""

from pydantic import BaseModel, Field
from agent_builder.builders.tool_builder import ToolBuilder
from app.database.workflow_queries import get_workflow_by_name
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GetWorkflowDetailsInput(BaseModel):
    """Input schema for get workflow details tool"""

    workflow_name: str = Field(
        description="The name of the workflow to get details for"
    )
    return_interactive_component: bool = Field(
        default=False,
        description="Set to true when user wants to see/view workflow details in a visual format. Set to false for simple text response.",
    )


# Global state to track interactive component requests
_last_interactive_workflow = None


async def get_workflow_details(
    workflow_name: str, return_interactive_component: bool = False
) -> str:
    """
    Get workflow details including code and input parameters

    Args:
        workflow_name: Name of the workflow
        return_interactive_component: If True, stores workflow for interactive display

    Returns:
        String containing workflow details
    """
    global _last_interactive_workflow

    try:
        workflow = await get_workflow_by_name(workflow_name)
        if not workflow:
            _last_interactive_workflow = None
            return f"Workflow '{workflow_name}' not found"

        # If interactive component requested, store the data
        if return_interactive_component:
            _last_interactive_workflow = {
                "name": workflow.name,
                "description": workflow.description or "No description",
                "code": workflow.code,
                "status": workflow.status,
                "endpoint": workflow.endpoint,
                "input_parameters": workflow.input_parameters,
            }
            logger.info(f"Stored workflow '{workflow_name}' for interactive component")

        details = f"""
Workflow: {workflow.name}
Status: {workflow.status}
Description: {workflow.description or 'No description available'}

Code:
{workflow.code}

Input Parameters (JSON Schema):
{workflow.input_parameters if workflow.input_parameters else 'No input parameters defined'}

Endpoint: {workflow.endpoint or 'No endpoint defined'}
"""
        return details

    except Exception as e:
        logger.error(f"Error getting workflow details: {str(e)}")
        _last_interactive_workflow = None
        return f"Error retrieving workflow details: {str(e)}"


def get_last_interactive_workflow():
    """Get the last stored workflow for interactive component"""
    global _last_interactive_workflow
    return _last_interactive_workflow


def clear_interactive_workflow():
    """Clear stored workflow"""
    global _last_interactive_workflow
    _last_interactive_workflow = None


def create_get_workflow_details_tool():
    """
    Build and return the get workflow details tool
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="get_workflow_details")
    tool_builder.set_function(get_workflow_details)
    tool_builder.set_coroutine(get_workflow_details)
    tool_builder.set_description(
        description=(
            """Get detailed information about a workflow including its code and input parameters.
            Use this tool when you need to understand what a workflow does or what inputs it requires.
            
            IMPORTANT: Set return_interactive_component=true when user wants to VIEW/SEE workflow details (e.g., "show me details of workflow X", "what does workflow Y do").
            Set return_interactive_component=false when checking workflow info for execution purposes."""
        )
    )
    tool_builder.set_schema(schema=GetWorkflowDetailsInput)
    return tool_builder.build()
