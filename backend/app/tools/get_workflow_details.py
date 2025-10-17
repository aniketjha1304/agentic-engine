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
    workflow_name: str = Field(description="The name of the workflow to get details for")


async def get_workflow_details(workflow_name: str) -> str:
    """
    Get workflow details including code and input parameters
    
    Args:
        workflow_name: Name of the workflow
        
    Returns:
        String containing workflow details
    """
    try:
        workflow = await get_workflow_by_name(workflow_name)
        if not workflow:
            return f"Workflow '{workflow_name}' not found"
        
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
        return f"Error retrieving workflow details: {str(e)}"


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
            Provide the workflow name to get its details."""
        )
    )
    tool_builder.set_schema(schema=GetWorkflowDetailsInput)
    return tool_builder.build()
