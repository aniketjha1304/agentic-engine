"""
List Workflows Tool - Returns all available workflows
"""

from pydantic import BaseModel, Field
from agent_builder.builders.tool_builder import ToolBuilder
from app.database.workflow_queries import get_all_workflows
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ListWorkflowsInput(BaseModel):
    """Input schema for list workflows tool"""

    return_interactive_component: bool = Field(
        default=False,
        description="Set to true when user wants to see/view workflows in a visual format. Set to false for simple text response.",
    )


# Global state to track interactive component requests
_last_interactive_workflows = None


async def list_workflows(return_interactive_component: bool = False) -> str:
    """
    List all available workflows

    Args:
        return_interactive_component: If True, stores workflows for interactive display

    Returns:
        String containing list of workflows
    """
    global _last_interactive_workflows

    try:
        workflows = await get_all_workflows()

        if not workflows:
            _last_interactive_workflows = None
            return "No workflows available."

        # If interactive component requested, store the data
        if return_interactive_component:
            _last_interactive_workflows = [
                {
                    "name": w.name,
                    "description": w.description or "No description",
                    "code": w.code,
                    "status": w.status,
                    "endpoint": w.endpoint,
                    "input_parameters": w.input_parameters,
                }
                for w in workflows
            ]
            logger.info(f"Stored {len(workflows)} workflows for interactive component")

        # Return text response
        response = f"Found {len(workflows)} workflows:\n\n"
        for w in workflows:
            response += f"• {w.name} ({w.status})"
            if w.description:
                response += f" - {w.description}"
            response += "\n"

        return response

    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        _last_interactive_workflows = None
        return f"Error retrieving workflows: {str(e)}"


def get_last_interactive_workflows():
    """Get the last stored workflows for interactive component"""
    global _last_interactive_workflows
    return _last_interactive_workflows


def clear_interactive_workflows():
    """Clear stored workflows"""
    global _last_interactive_workflows
    _last_interactive_workflows = None


def create_list_workflows_tool():
    """
    Build and return the list workflows tool
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="list_workflows")
    tool_builder.set_function(list_workflows)
    tool_builder.set_coroutine(list_workflows)
    tool_builder.set_description(
        description=(
            """List all available workflows/skills that can be used.
            Use this tool when the user asks to see, show, list, or view available workflows.
            
            IMPORTANT: Set return_interactive_component=true when user wants to VIEW/SEE workflows (e.g., "show me workflows", "what workflows are available", "list all workflows").
            Set return_interactive_component=false for simple questions about workflow count or existence."""
        )
    )
    tool_builder.set_schema(schema=ListWorkflowsInput)
    return tool_builder.build()
