"""
Tool: ProposeWorkflow

Lets Ada propose (draft) a workflow by collecting its state (title, description, code, etc)
for human/UI review, without saving or validating it yet.

"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from agent_builder.builders.tool_builder import ToolBuilder


class ProposeWorkflowInput(BaseModel):
    title: str = Field(description="The suggested workflow title.")
    description: str = Field(
        description="Detailed description of function and purpose."
    )
    code: str = Field(description="Workflow Python code to be reviewed by a human.")
    workflow_input_signature: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="JSON Schema describing expected input parameters for the workflow.",
    )
    status: str = Field(
        default="inactive",
        description="The workflow status, always proposed as 'inactive'.",
    )


def build_propose_workflow_tool(workflow_manager) -> dict:
    """
    Construct and return the propose workflow tool.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="ProposeWorkflow")
    tool_builder.set_function(workflow_manager.populate_state)
    tool_builder.set_coroutine(workflow_manager.populate_state)
    tool_builder.set_description(
        description=(
            """Collect a new or updated workflow state and store it for UI/human review,
            without saving or validating. The workflow will be 'inactive' and ready for review/confirmation.
            """
        )
    )
    tool_builder.set_schema(schema=ProposeWorkflowInput)
    return tool_builder.build()
