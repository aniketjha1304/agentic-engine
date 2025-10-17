"""
Tool: UpdateWorkflow

Lets Ada update an existing HTTP-triggered workflow by title.
Updates only description, input signature, and code. Validates code before save.
Status will always be set to 'inactive'.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from agent_builder.builders.tool_builder import ToolBuilder


class UpdateWorkflowInput(BaseModel):
    workflow_title: str = Field(description="The title of the workflow to update.")
    new_description: Optional[str] = Field(
        default=None, description="New description, if updating."
    )
    new_code: Optional[str] = Field(
        default=None, description="New Python code, if updating."
    )
    new_workflow_input_signature: Optional[Dict[str, Any]] = Field(
        default=None,
        description="(Optional) New JSON schema for workflow input parameters.",
    )


def build_update_workflow_tool(workflow_manager) -> dict:
    """
    Construct and return the update workflow tool.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="UpdateWorkflow")
    tool_builder.set_function(workflow_manager.update_workflow)
    tool_builder.set_coroutine(workflow_manager.update_workflow)
    tool_builder.set_description(
        description=(
            """Update an existing workflow in the system.
            Only description, input signature, and code can be modified.
            The workflow will be forced to 'Inactive' after update. 
            Workflow code will be validated prior to saving."""
        )
    )
    tool_builder.set_schema(schema=UpdateWorkflowInput)
    return tool_builder.build()
